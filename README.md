# Formation flight UAV control system

Currently based on computer vision and GPS


# MAVLink APIs

## Mavlink commands

This method requires us to write our own comms protocol but we might be able to use PyMAVLinks protocol

https://mavlink.io/en/messages/ardupilotmega.html#PLANE_MODE

## Drone Kit (has python wrapper)

I (Alvaro) am leaning mostly towards this one. [This](https://dronekit-python.readthedocs.io/en/latest/guide/copter/guided_mode.html) document has a lot of information about controlling it. There seems to be an option for controlling accelerations but this one doesn't work so we might need to modify deflections.

On the other hand, it seems like it is mostly for quadcopters meaning we might need to make our own conection using the Mavlink commands.

https://github.com/dronekit/dronekit-python

## Pymavlink (has python wrapper)

We could use its protocol to communicate and send custom commands

https://github.com/ArduPilot/pymavlink

# DREF information


https://developer.x-plane.com/datarefs/
