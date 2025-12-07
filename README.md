This folder contains scripts for running CARLA in headless mode.

## File structure
ROOT  
ROOT/Carla  
ROOT/Autonomous-Driving-in-Carla-using-Deep-Reinforcement-Learning

## Entry script
run.sh (change ROOT directory here)

## Known errors
Sometimes I get the following error. Rerunning the script seems to help...
```
Client version: 0.9.16
ERROR:root:Connection has been refused by the server.

Exit
Traceback (most recent call last):
  File "/lus/eagle/projects/datascience_collab/eku/Carla_RL/continuous_driver.py", line 297, in <module>
    runner()
  File "/lus/eagle/projects/datascience_collab/eku/Carla_RL/continuous_driver.py", line 115, in runner
    env = CarlaEnvironment(client, world,town, checkpoint_frequency=None)
```