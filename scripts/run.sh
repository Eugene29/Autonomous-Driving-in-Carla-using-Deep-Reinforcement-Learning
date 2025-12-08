#!/usr/bin/env bash
set -euo pipefail

# Kill any existing Carla processes and free the port
pkill -9 -f CarlaUE4 2>/dev/null || true
fuser -k 2000/tcp 2>/dev/null || true
sleep 2

ROOT="/lus/eagle/projects/datascience_collab/eku/Carla_RL"
# ROOT="<Your ROOT folder>"
cd $ROOT
module load conda
conda activate carla

# Configuration (override with env vars)
CARLA_PORT=${CARLA_PORT:-2000}
CARLA_HOST=${CARLA_HOST:-localhost}
export CARLA_VIDEO_PATH=${CARLA_VIDEO_PATH:-"figs/run.mp4"}
mkdir -p figs

# Launch CARLA server headless
DISPLAY=${DISPLAY-} ./Carla/CarlaUE4.sh -RenderOffScreen -nosound -carla-rpc-port=${CARLA_PORT} &
SERVER_PID=$!
trap 'kill ${SERVER_PID} 2>/dev/null || true' EXIT
echo "Started CARLA server (pid ${SERVER_PID}) on ${CARLA_HOST}:${CARLA_PORT}"

# Run the driver (set --train True to train)
rm $CARLA_VIDEO_PATH &> /dev/null || true
python continuous_driver.py --exp-name ppo --train False --town Town02 --test-timesteps 300