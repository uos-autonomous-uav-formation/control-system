import busio
import board
import numpy as np
from pymavlink import mavutil
from src.computervision import ObjectDetection, MODEL_WEIGTS_DIR_DRACO
from src.controlsystem import dist_from_width, angle_from_xoff
from src.mavlink import MavlinkConn, RASPI
from picamera2 import Picamera2
from libcamera import Transform
from src.pid import PID
import time
from src.aoa_sensor import *
from src.vortex.Vortex import moving_ave, state_count, state_iden

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
    # TODO: Start with the initial conditions when engaded

    mavlink = MavlinkConn(RASPI)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 30)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 30)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_SYSTEM_TIME, 10)
    print("Mavlink initiated")


    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={"size": (1920, 1082)}, transform=Transform(180))
    picam2.configure(camera_config)
    picam2.start()
    print("Camera initiated")

    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    aoa_r = AoaSensor(2, spi, board.D20, 5, AoA2_conf)
    aoa_l = AoaSensor(1, spi, board.D7, 5, AoA1_conf)
    print("AoA sensors initiated")

    cv = ObjectDetection(MODEL_WEIGTS_DIR_DRACO)
    throttle_controller = PID(0.006, 0.00004, 0, 0)
    print("Preflight checks complete, starting controller")

    while True:

        img = picam2.capture_array()

        leaders = cv.process(img)

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

                    for i in range(5):
                        # Used on the aircraft
                        a_angle = mavlink.recover_data("ATTITUDE")[0]["pitch"]
                        reading_l = aoa_l.alpha_aoa(mavlink.recover_data("VFR_HUD")[0]["airspeed"])
                        reading_r = aoa_r.alpha_aoa(mavlink.recover_data("VFR_HUD")[0]["airspeed"])
                        ave_l, ave_r, diff_ave = moving_ave(reading_l, reading_r, a_angle, n_mov)
                        end = time.time()

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

