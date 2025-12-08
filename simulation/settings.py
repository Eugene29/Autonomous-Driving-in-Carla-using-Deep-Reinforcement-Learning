'''
All the parameters used in the Simulation has been documented here.

Easily modifiable paramters with the quick access in this settings.py file \
    to achieve quick modifications especially during the training sessions.

Names of the parameters are self-explanatory therefore elimating the use of further comments.
'''


HOST = "localhost"
PORT = 2000
TIMEOUT = 5.0

CAR_NAME = 'model3'
EPISODE_LENGTH = 120
NUMBER_OF_VEHICLES = 30
NUMBER_OF_PEDESTRIAN = 10
CONTINUOUS_ACTION = True
VISUAL_DISPLAY = False  # keep headless-safe; set True to open pygame window


# Sensor shorthands (expanded in sensors.py via SENSOR_MAP)
# Options: rgb, ssc, depth, instance, optical_flow, normals, lidar, radar, dvs
MODEL_SENSORS = ['ssc']           # Input to RL model (first one -> front_camera)
VISUAL_SENSORS = ['ssc', 'rgb']   # Saved to video for visualization

# Sensor resolutions
MODEL_RES = (160, 80)             # Small for fast NN processing
VISUAL_RES = (854, 480)           # Larger for clear visualization