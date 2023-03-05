import numpy as np

from src.computervision import ObjectDetection, load_img_from_file, liveframe, grab_screen_frame
from src.flightsim import *
from src.mavlink import SIMULATOR_ADDRS
from pymavlink import mavutil
import cv2

import time
from pymavlink.quaternion import QuaternionBase
import math

TARGET_Y = 540
TARGET_X = 960


def wait_heartbeat(m):
    """wait for a heartbeat so we know the target system IDs"""
    print("Waiting for APM heartbeat")

    print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_component))


# NOTE THIS IF IS MANDATORY!!!!! REMOVING IT WILL BREAK PARALELISM
if __name__ == '__main__':
    boot_time = time.time()
    pitch = 0
    roll = 0

    mavlink = mavutil.mavlink_connection(SIMULATOR_ADDRS, baud=57600, source_system=255)
    wait_heartbeat(mavlink)

    sim = Simulator()
    sim_process = cone_leadergen(sim, 1, min_distance=5, max_distance=7, angle=0).load_leader()

    cv = ObjectDetection()

    def loop(img: np.ndarray) -> np.ndarray:
        global pitch, roll

        leaders = cv.process(img)

        cv2.circle(img, center=(TARGET_X, TARGET_Y), radius=10, color=(255,0,0), thickness=1)

        if len(leaders) > 0:
            pitch = 0.05 * (TARGET_Y - leaders[0].center_y)
            roll = -0.05 * (TARGET_X - leaders[0].center_x)
            img = leaders[0].render(img)

        print(pitch)

        mavlink.mav.set_attitude_target_send(
            int(1e3 * (time.time() - boot_time)), # ms since boot
            mavlink.target_system, mavlink.target_component,
            mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_BODY_YAW_RATE_IGNORE,
            # -> attitude quaternion (w, x, y, z | zero-rotation is 1, 0, 0, 0)
            QuaternionBase([math.radians(angle) for angle in (roll, pitch, 0)]),
            0, 0, 0, 100 # roll rate, pitch rate, yaw rate, thrust
        )

        return img

    liveframe(loop, left=-1920)

    sim_process.join()
