import numpy as np
from pymavlink import mavutil
from src.computervision import ObjectDetection, liveframe, MODEL_WEIGTS_DIR_CESSNA
from src.controlsystem import dist_from_width, angle_from_xoff, xoff_from_angle
from src.flightsim import *
from src.mavlink import MavlinkConn, SIMULATOR_ADDRS
import cv2

import time

TARGET_DIST = 6
TARGET_YAW = 13
TARGET_PITCH = 0


def wait_heartbeat(m):
    """wait for a heartbeat so we know the target system IDs"""
    print("Waiting for APM heartbeat")

    print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_component))


# NOTE THIS IF IS MANDATORY!!!!! REMOVING IT WILL BREAK PARALELISM
if __name__ == '__main__':
    boot_time = time.time()
    # TODO: Start with the initial conditions when engaded

    sim = Simulator()
    sim_process = cone_leadergen(sim, 1, min_distance=3, max_distance=5, angle=0.2).load_leader()

    mavlink = MavlinkConn(SIMULATOR_ADDRS)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 30)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 30)

    cv = ObjectDetection(MODEL_WEIGTS_DIR_CESSNA)


    def loop(img: np.ndarray) -> np.ndarray:
        global pitch, roll, mavlink

        leaders = cv.process(img)

        cv2.circle(img, center=(int(img.shape[1] * xoff_from_angle(TARGET_YAW)), int(img.shape[0] * xoff_from_angle(TARGET_PITCH))), radius=10, color=(255, 0, 0), thickness=1)

        if len(leaders) > 0:
            aprox_dist = dist_from_width(leaders[0].width_non_dimensional)
            dyaw_angle = angle_from_xoff(leaders[0].center_x_non_dimensional)
            dpitch_angle = angle_from_xoff(leaders[0].center_y_non_dimensional)

            pitch = dpitch_angle - TARGET_PITCH
            roll = 2 * (TARGET_YAW - dyaw_angle)
            throttle = 0.018 * (aprox_dist - TARGET_DIST) + 0.5

            print(throttle)
            throttle = np.clip(throttle, 0.3, 0.8)
            print(throttle, (aprox_dist - TARGET_DIST))
            roll = np.clip(roll, -15, 10)

            with open("flight.csv", "a") as f:
                f.write(f"{aprox_dist},{dyaw_angle},{dpitch_angle},{pitch},{roll},{throttle},{leaders[0].confidence}\n")

            img = leaders[0].render(img)

            mavlink.set_change_in_attitude(roll, pitch, 0, throttle)

        # TODO: If on guided mode but don't detect leader for a long time switch flight mode to a safe one

        return img


    liveframe(loop, left=-1920)

    sim_process.join()
