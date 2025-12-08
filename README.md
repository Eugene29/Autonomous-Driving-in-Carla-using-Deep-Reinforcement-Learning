This folder contains scripts for running CARLA in headless mode.

## Additional dependency (Carla)
ROOT/Carla

## Entry script
run.sh (change ROOT directory in here)

## Known errors
It takes a couple tries for the client to connect to Carla server.
```
INFO:root:Connecting to Carla server. This may take awhile...
Failed to make a connection with the server: time-out of 30000ms while waiting for the simulator, make sure the simulator is ready and connected to localhost:2000

Client version: 0.9.16
WARNING:root:Connection failed. Retrying...
INFO:root:Connection established successfully.
```
