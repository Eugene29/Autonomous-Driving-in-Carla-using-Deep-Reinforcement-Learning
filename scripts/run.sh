#!/usr/bin/env bash
set -euo pipefail

# Kill any existing Carla processes and free the port
pkill -9 -f CarlaUE4 2>/dev/null || true
fuser -k 2000/tcp 2>/dev/null || true
sleep 2

ROOT="<Your ROOT folder>"
cd $ROOT
module load conda
conda activate carla

# Configuration (override with env vars)
CARLA_PORT=${CARLA_PORT:-2000}
CARLA_HOST=${CARLA_HOST:-localhost}
FRAME_DIR=${CARLA_FRAME_DIR:-frames}
OUTPUT_VIDEO=${OUTPUT_VIDEO:-run.mp4}
FPS=${CARLA_FRAME_FPS:-10}

# Launch CARLA server headless
DISPLAY=${DISPLAY-} ./Carla/CarlaUE4.sh -RenderOffScreen -nosound -carla-rpc-port=${CARLA_PORT} &
SERVER_PID=$!
trap 'kill ${SERVER_PID} 2>/dev/null || true' EXIT
echo "Started CARLA server (pid ${SERVER_PID}) on ${CARLA_HOST}:${CARLA_PORT}"

# Give the server a moment to come up
sleep 10

# Run the driver (set --train True to train)
cd $ROOT/Autonomous-Driving-in-Carla-using-Deep-Reinforcement-Learning
rm ./frames/*.png
python continuous_driver.py --exp-name ppo --train False --town Town02 --test-timesteps 100

# Assemble frames into a video without ffmpeg (uses OpenCV)
python $ROOT/assemble_video.py "$FRAME_DIR" "$OUTPUT_VIDEO" "$FPS"