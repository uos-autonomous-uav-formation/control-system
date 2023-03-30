import numpy as np
from pymavlink import mavutil
from src.computervision import ObjectDetection, liveframe, MODEL_WEIGTS_DIR_CESSNA
from src.flightsim import *
from src.mavlink import MavlinkConn, SIMULATOR_ADDRS
import cv2

import time

TARGET_Y = 540
TARGET_X = 960


def wait_heartbeat(m):
    """wait for a heartbeat so we know the target system IDs"""
    print("Waiting for APM heartbeat")

    print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_component))


# NOTE THIS IF IS MANDATORY!!!!! REMOVING IT WILL BREAK PARALELISM
if __name__ == '__main__':
    boot_time = time.time()
    # TODO: Start with the initial conditions when engaded

    sim = Simulator()
    sim_process = cone_leadergen(sim, 1, min_distance=3, max_distance=5, angle=0).load_leader()

    mavlink = MavlinkConn(SIMULATOR_ADDRS)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 2)

    cv = ObjectDetection(MODEL_WEIGTS_DIR_CESSNA)


    def loop(img: np.ndarray) -> np.ndarray:
        global pitch, roll, mavlink

        leaders = cv.process(img)

        cv2.circle(img, center=(TARGET_X, TARGET_Y), radius=10, color=(255, 0, 0), thickness=1)

        if len(leaders) > 0:
            pitch = 0.04 * (TARGET_Y - leaders[0].center_y)
            roll = -0.05 * (TARGET_X - leaders[0].center_x)
            throttle = 0.5 * (200 - leaders[0].width)
            print(leaders[0].width)

            img = leaders[0].render(img)

            mavlink.set_attitude(roll, pitch, 0, throttle)

        # TODO: If on guided mode but don't detect leader for a long time switch flight mode to a safe one

        return img


    liveframe(loop, left=-1920)

    sim_process.join()
