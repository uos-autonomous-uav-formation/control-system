import numpy as np
from pymavlink import mavutil
from src.computervision import ObjectDetection, liveframe, MODEL_WEIGTS_DIR_CESSNA, MODEL_WEIGTS_DIR_DRACO
from src.controlsystem import dist_from_width, angle_from_xoff, xoff_from_angle
from src.flightsim import *
from src.mavlink import MavlinkConn, SIMULATOR_ADDRS
import cv2
from src.vortex.Vortex import *
from src.vortex.Vortex_Sim import *
from src.vortex.sim import model
import time

from src.pid import PID

TARGET_DIST = 6
TARGET_YAW = 13
TARGET_PITCH = 0
REF_THROTTLE = 0.5
pos = 10
atm_var1 = [1]
atm_var2 = [1]
reading_std = 0.1
n_mov = 10
ideal_span_sep = 1.6

# NOTE THIS IF IS MANDATORY!!!!! REMOVING IT WILL BREAK PARALELISM
if __name__ == '__main__':
    boot_time = time.time()

    sim = Simulator()
    sim_process = cone_leadergen(sim, 1, min_distance=3, max_distance=5, angle=0.2).load_leader()

    mavlink = MavlinkConn(SIMULATOR_ADDRS)
    # TODO: Slow these down depending on how long the loop takes
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 30)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 30)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_SYSTEM_TIME, 10)

    cv = ObjectDetection(MODEL_WEIGTS_DIR_CESSNA)

    throttle_controller = PID(0.006, 0.00004, 0, 0)

    sim = Simulator()
    sim.add_freq_value(DREFs.multiplayer.lon, 60)
    sim.add_freq_value(DREFs.long, 60)
    sim.add_freq_value(DREFs.multiplayer.lat, 60)
    sim.add_freq_value(DREFs.lat, 60)


    def loop(img: np.ndarray) -> np.ndarray:
        global pitch, roll, mavlink, TARGET_YAW, TARGET_DIST, TARGET_DIST

        start = time.time()

        leaders = cv.process(img)

        cv2.circle(img, center=(
            int(img.shape[1] * xoff_from_angle(TARGET_YAW)), int(img.shape[0] * xoff_from_angle(TARGET_PITCH))),
                   radius=10,
                   color=(255, 0, 0), thickness=1)

        mavlink.send_heatbeat()
        mavlink.corrected_timestamp()

        if len(leaders) > 0:
            # Translate computer vision to approximate positions
            aprox_dist = dist_from_width(leaders[0].width_non_dimensional)
            dyaw_angle = angle_from_xoff(leaders[0].center_x_non_dimensional)
            dpitch_angle = angle_from_xoff(leaders[0].center_y_non_dimensional)

            # Calculate errors from target positions and scaling factors prior to control system
            pitch = dpitch_angle - TARGET_PITCH
            roll = 1.7 * (TARGET_YAW - dyaw_angle)
            throttle = throttle_controller.controller(aprox_dist - TARGET_DIST, 20)

            mavlink.send_float("2CVDIST", aprox_dist * 10)

            # Safety constrain
            if aprox_dist < 4:
                pitch = 8
                throttle = 0

            img = leaders[0].render(img)

            mavlink.set_change_in_attitude(roll, pitch, 0, throttle + REF_THROTTLE, roll_limit=(-15, 6),
                                           throttle_limit=(0.1, 0.70))

            # TODO: If on guided mode but don't detect leader for a long time switch flight mode to a safe one

            try:
                if aprox_dist < 15:
                    state_array = np.zeros(4)
                    statelist = []

                    start1 = time.time()

                    for i in range(5):
                        # Used on the aircraft
                        a_angle = mavlink.recover_data("ATTITUDE")[0]["pitch"]
                        reading_l = model(sim)[0]
                        reading_r = model(sim)[1]
                        ave_l, ave_r, diff_ave = moving_ave(reading_l, reading_r, a_angle, n_mov)
                        end = time.time()

                    time1 = time.time() - start1

                    if -(reading_std / 2) < diff_ave < (reading_std / 2) and -(reading_std / 2) < ave_l < (
                            reading_std / 2) and -(reading_std / 2) < ave_r < (
                            reading_std / 2):  # to determine constraints if too far
                        state = 1
                    elif diff_ave > (reading_std / 2) and ave_l > (reading_std / 2) and ave_r > 0.1:
                        state = 2
                    elif diff_ave < -(reading_std / 2) and ave_l < -(reading_std / 2) and ave_r > ave_l:
                        state = 3
                    else:
                        state = 4

                    statelist.append(state)
                    state_array = state_count(statelist)

                    TARGET_YAW = state_iden(state_array, TARGET_YAW, ave_l, ideal_span_sep)
                else:
                    ave_l = 0
                    ave_r = 0
                    diff_ave = 0
            except Exception as e:
                ave_l = -1
                ave_r = -1
                diff_ave = -1
                TARGET_YAW = 13

            with open("flight.csv", "a") as f:
                f.write(
                    f"{mavlink.corrected_timestamp()},{aprox_dist},{dyaw_angle},{dpitch_angle},{pitch},{roll},{throttle},{leaders[0].confidence},{TARGET_YAW},{ave_l},{ave_r},{diff_ave}\n")


        else:
            print("Controller failed")

        # print(time.time() - start - time1)
        # else:
        #     mavlink.set_change_in_attitude(0, 0, 0, REF_THROTTLE, roll_limit=(-15, 6), throttle_limit=(0.1, 0.65))

        return img


    liveframe(loop, left=-1920)

    # sim_process.join()
