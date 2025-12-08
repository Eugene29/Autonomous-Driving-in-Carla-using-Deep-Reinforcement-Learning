import math
import os
import threading
import numpy as np
import weakref
import pygame
import imageio
from simulation.connection import carla
from simulation.settings import MODEL_RES, VISUAL_RES

# Optional video output path (set to None or empty to disable recording)
VIDEO_OUTPUT_PATH = os.environ.get("CARLA_VIDEO_PATH", "output.mp4")

# Shorthand -> full CARLA sensor name
SENSOR_MAP = {
    'rgb': 'sensor.camera.rgb',
    'ssc': 'sensor.camera.semantic_segmentation',
    'depth': 'sensor.camera.depth',
    'instance': 'sensor.camera.instance_segmentation',
    'optical_flow': 'sensor.camera.optical_flow',
    'normals': 'sensor.camera.normals',
    'lidar': 'sensor.lidar.ray_cast',
    'lidar_semantic': 'sensor.lidar.ray_cast_semantic',
    'radar': 'sensor.other.radar',
    'dvs': 'sensor.camera.dvs',
}


# ---------------------------------------------------------------------|
# ------------------------------- SENSOR |
# ---------------------------------------------------------------------|

class Sensor:

    def __init__(self, vehicle, model_sensors: list[str], visual_sensors: list[str] = None):
        self.parent = vehicle
        self.model_sensors = model_sensors
        self.visual_sensors = visual_sensors or []

        # Separate frame buffers for model (low res) and visual (high res)
        self.model_frames = {s: [] for s in model_sensors}
        self.visual_frames = {s: [] for s in self.visual_sensors}

        # Video writer (initialized on first frame)
        self._video_writer = None
        self._video_lock = threading.Lock()  # Prevent concurrent writes from multiple sensor threads

        # All sensor actors (for cleanup)
        self._all_sensors = []

        world = self.parent.get_world()
        weak_self = weakref.ref(self)

        # Create low-res sensors for model input
        for sensor_type in model_sensors:
            sensor = self._create_sensor(world, sensor_type, MODEL_RES)
            self._all_sensors.append(sensor)
            sensor.listen(lambda img, st=sensor_type: Sensor._on_model_image(weak_self, img, st))

        # Create high-res sensors for visualization (separate instances, third-person view)
        for sensor_type in self.visual_sensors:
            sensor = self._create_sensor(world, sensor_type, VISUAL_RES, third_person=True)
            self._all_sensors.append(sensor)
            sensor.listen(lambda img, st=sensor_type: Sensor._on_visual_image(weak_self, img, st))

        # Backwards compatibility: front_camera points to first model sensor's frames
        self.front_camera = self.model_frames[model_sensors[0]]
        # Backwards compatibility: sensor points to first model sensor
        self.sensor = self._all_sensors[0]
        # Legacy alias
        self.frames = self.model_frames

    def _create_sensor(self, world, sensor_type, resolution, third_person=False):
        full_name = SENSOR_MAP.get(sensor_type, sensor_type)
        bp = world.get_blueprint_library().find(full_name)
        bp.set_attribute('image_size_x', str(resolution[0]))
        bp.set_attribute('image_size_y', str(resolution[1]))
        bp.set_attribute('fov', '110' if third_person else '125')
        if third_person:
            # Behind and above the vehicle, looking down
            transform = carla.Transform(carla.Location(x=-6.0, z=3.5), carla.Rotation(pitch=-15))
        else:
            # Front-facing camera for model input
            transform = carla.Transform(carla.Location(x=2.4, z=1.5), carla.Rotation(pitch=-10))
        return world.spawn_actor(bp, transform, attach_to=self.parent)

    def get_all_sensors(self):
        """Return all sensor actors for cleanup."""
        return self._all_sensors

    def release_video(self):
        """Finalize and close the video file."""
        if self._video_writer is not None:
            self._video_writer.close()
            self._video_writer = None
            print(f"Video saved: {os.path.abspath(VIDEO_OUTPUT_PATH)}")

    @staticmethod
    def _on_model_image(weak_self, image, sensor_type):
        self = weak_self()
        if not self:
            return
        if sensor_type in ('ssc', 'instance'):
            image.convert(carla.ColorConverter.CityScapesPalette)
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
        rgb = arr[:, :, :3][:, :, ::-1].copy()
        self.model_frames[sensor_type].append(rgb)

    @staticmethod
    def _on_visual_image(weak_self, image, sensor_type):
        self = weak_self()
        if not self:
            return
        if sensor_type in ('ssc', 'instance'):
            image.convert(carla.ColorConverter.CityScapesPalette)
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
        rgb = arr[:, :, :3][:, :, ::-1].copy()
        self.visual_frames[sensor_type].append(rgb)
        # Write frame to video
        if VIDEO_OUTPUT_PATH:
            self._write_video_frame()

    def _write_video_frame(self):
        """Write combined visual sensors to video using ffmpeg."""
        if not all(len(self.visual_frames[s]) > 0 for s in self.visual_sensors):
            return
        combined = np.hstack([self.visual_frames[s][-1] for s in self.visual_sensors])
        # Use lock to prevent concurrent writes from multiple sensor threads
        with self._video_lock:
            # Initialize video writer on first frame (H.264 via ffmpeg)
            if self._video_writer is None:
                self._video_writer = imageio.get_writer(
                    VIDEO_OUTPUT_PATH,
                    fps=20,
                    codec='libx264',
                    pixelformat='yuv420p',
                    macro_block_size=1,  # Avoid resizing for non-16-divisible dimensions
                    output_params=['-preset', 'fast']
                )
            self._video_writer.append_data(combined)


# ---------------------------------------------------------------------|
# ------------------------------- ENV CAMERA |
# ---------------------------------------------------------------------|

class CameraSensorEnv:

    def __init__(self, vehicle):

        pygame.init()
        self.display = pygame.display.set_mode((720, 720),pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.sensor_name = SENSOR_MAP['rgb']
        self.parent = vehicle
        self.surface = None
        world = self.parent.get_world()
        self.sensor = self._set_camera_sensor(world)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda image: CameraSensorEnv._get_third_person_camera(weak_self, image))

    # Third camera is setup and provide the visual observations for our environment.

    def _set_camera_sensor(self, world):

        thrid_person_camera_bp = world.get_blueprint_library().find(self.sensor_name)
        thrid_person_camera_bp.set_attribute('image_size_x', f'720')
        thrid_person_camera_bp.set_attribute('image_size_y', f'720')
        third_camera = world.spawn_actor(thrid_person_camera_bp, carla.Transform(
            carla.Location(x=-4.0, z=2.0), carla.Rotation(pitch=-12.0)), attach_to=self.parent)
        return third_camera

    @staticmethod
    def _get_third_person_camera(weak_self, image):
        self = weak_self()
        if not self:
            return
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        placeholder1 = array.reshape((image.width, image.height, 4))
        placeholder2 = placeholder1[:, :, :3]
        placeholder2 = placeholder2[:, :, ::-1]
        self.surface = pygame.surfarray.make_surface(placeholder2.swapaxes(0, 1))
        self.display.blit(self.surface, (0, 0))
        pygame.display.flip()



# ---------------------------------------------------------------------|
# ------------------------------- COLLISION SENSOR|
# ---------------------------------------------------------------------|

# It's an important as it helps us to tract collisions
# It also helps with resetting the vehicle after detecting any collisions
class CollisionSensor:

    def __init__(self, vehicle) -> None:
        self.sensor_name = 'sensor.other.collision'
        self.parent = vehicle
        self.collision_data = list()
        world = self.parent.get_world()
        self.sensor = self._set_collision_sensor(world)
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda event: CollisionSensor._on_collision(weak_self, event))

    # Collision sensor to detect collisions occured in the driving process.
    def _set_collision_sensor(self, world) -> object:
        collision_sensor_bp = world.get_blueprint_library().find(self.sensor_name)
        sensor_relative_transform = carla.Transform(
            carla.Location(x=1.3, z=0.5))
        collision_sensor = world.spawn_actor(
            collision_sensor_bp, sensor_relative_transform, attach_to=self.parent)
        return collision_sensor

    @staticmethod
    def _on_collision(weak_self, event):
        self = weak_self()
        if not self:
            return
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x ** 2 + impulse.y ** 2 + impulse.z ** 2)
        self.collision_data.append(intensity)
