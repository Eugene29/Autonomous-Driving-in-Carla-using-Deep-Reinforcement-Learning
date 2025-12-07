#!/usr/bin/env python3
"""
Assemble a folder of PNG frames into an MP4 using ffmpeg.
Usage: python assemble_video.py <frame_dir> <output_file> <fps>
Defaults: frame_dir="frames", output_file="run.mp4", fps=20
"""
import glob
import os
import subprocess
import sys

try:
    import imageio_ffmpeg
except ImportError as exc:
    sys.exit(f"imageio_ffmpeg not available: {exc}")


def assemble(frame_dir: str = "frames", output_file: str = "run.mp4", fps: float = 20) -> None:
    frames = sorted(glob.glob(os.path.join(frame_dir, "*.png")))
    if not frames:
        sys.exit(f"No frames found in {frame_dir}")

    if not frames:
        print(f"No images found in {frame_dir}/")
        return

    # Use imageio_ffmpeg for H.264 encoding (VSCode compatible)
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    # ffmpeg command: read images, encode as H.264
    cmd = [
        ffmpeg_path,
        '-y',  # overwrite output
        '-framerate', str(fps),
        '-pattern_type', 'glob',
        '-i', f'{frame_dir}/*.png',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',  # compatibility
        '-preset', 'fast',
        output_file
    ]

    print(f"Creating video with ffmpeg (H.264)...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ffmpeg failed: {result.stderr}")
        return

    print(f"Video saved: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        assemble()
    elif len(sys.argv) == 4:
        assemble(sys.argv[1], sys.argv[2], float(sys.argv[3]))
    else:
        sys.exit("usage: python assemble_video.py [frame_dir output_file fps]")
