This folder contains scripts for running CARLA in headless mode.

## Additional dependency (Carla)
ROOT/Carla

## Entry script
run.sh (change ROOT directory in here)

## Known errors
Sometimes I get the following error (especially the first time I run it). Rerunning the script seems to fix it...
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
