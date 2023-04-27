import numpy as np
from pymavlink import mavutil
from src.computervision import ObjectDetection, MODEL_WEIGTS_DIR_CESSNA, MODEL_WEIGTS_DIR_DRACO
from src.controlsystem import dist_from_width, angle_from_xoff, xoff_from_angle
from src.mavlink import MavlinkConn, SIMULATOR_ADDRS, RASPI
import cv2
from picamera2 import Picamera2
from libcamera import Transform
from src.pid import PID
import time

TARGET_DIST = 6
TARGET_YAW = 13
TARGET_PITCH = 0
REF_THROTTLE = 0.5


def wait_heartbeat(m):
    """wait for a heartbeat so we know the target system IDs"""
    print("Waiting for APM heartbeat")

    print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_component))


# NOTE THIS IF IS MANDATORY!!!!! REMOVING IT WILL BREAK PARALELISM
if __name__ == '__main__':
    boot_time = time.time()
    # TODO: Start with the initial conditions when engaded

    mavlink = MavlinkConn(RASPI)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 30)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 30)

    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={"size": (1920, 1082)}, transform=Transform(180))
    picam2.configure(camera_config)
    picam2.start()

    cv = ObjectDetection(MODEL_WEIGTS_DIR_DRACO)

    throttle_controller = PID(0.006, 0, 0, 0)

    while True:

        img = picam2.capture_array()

        leaders = cv.process(img)

        if len(leaders) > 0:
            # Translate computer vision to approximate positions
            aprox_dist = dist_from_width(leaders[0].width_non_dimensional)
            dyaw_angle = angle_from_xoff(leaders[0].center_x_non_dimensional)
            dpitch_angle = angle_from_xoff(leaders[0].center_y_non_dimensional)
	   
            # Calculate errors from target positions and scaling factors prior to control system
            pitch = dpitch_angle - TARGET_PITCH
            roll = 1.7 * (TARGET_YAW - dyaw_angle)
            throttle = throttle_controller.controller(aprox_dist - TARGET_DIST, 8)
            
            mavlink.send_float("CVDIST", aprox_dist)
            mavlink.send_msg(str(aprox_dist))

            # Safety constrain
            if aprox_dist < 4:
                pitch = 8
                throttle = 0

            with open("flight.csv", "a") as f:
                f.write(f"{aprox_dist},{dyaw_angle},{dpitch_angle},{pitch},{roll},{throttle},{leaders[0].confidence}\n")

            mavlink.set_change_in_attitude(roll, pitch, 0, throttle + REF_THROTTLE, roll_limit=(-15, 6), throttle_limit=(0.1, 0.65))
           
            # TODO: If on guided mode but don't detect leader for a long time switch flight mode to a safe one

        mavlink.send_heatbeat()


    liveframe(loop, left=-1920)

    # sim_process.join()
