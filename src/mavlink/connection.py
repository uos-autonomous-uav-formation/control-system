from __future__ import annotations

import numpy as np
from pymavlink import mavutil
from pymavlink.quaternion import QuaternionBase
from datetime import datetime
import time
import math


class MavlinkConn:
    last_heartbeat: datetime
    boot_time: float
    _data: dict[str, dict] = {}
    _offset: int = 0

    def __init__(self, device: str):
        self._mavlink = mavutil.mavlink_connection(device, baud=57600, source_system=2)
        self.boot_time = time.time()

    def corrected_timestamp(self):
        depoch, was_updated = self.recover_data("SYSTEM_TIME")
        depoch = depoch['time_unix_usec']

        if was_updated:
            self._offset = depoch - int(time.time() * 1e6)

        return int(time.time() * 1e6 + self._offset)

    def send_heatbeat(self):
        self._mavlink.mav.heartbeat_send(
            18,  # MAVTYPE =
            8,  # MAVAUTOPILOT
            8,  # MAV_MODE =
            8, 4)  # MAVSTATE =

    def set_attitude(self, roll, pitch, yaw, throttle):
        self._mavlink.mav.set_attitude_target_send(
            int(1e3 * (time.time() - self.boot_time)),  # ms since boot
            self._mavlink.target_system, self._mavlink.target_component,
            mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_BODY_YAW_RATE_IGNORE,
            # -> attitude quaternion (w, x, y, z | zero-rotation is 1, 0, 0, 0)
            QuaternionBase([math.radians(angle) for angle in (roll, pitch, yaw)]),
            0, 0, 0, throttle  # roll rate, pitch rate, yaw rate, thrust
        )

    def set_change_in_attitude(self, droll, dpitch, dyaw, dthrottle, roll_limit: tuple[float, float] = None,
                               pitch_limit=None,
                               throttle_limit: tuple[float, float] = None,
                               speed_limit: float | None = None):
        attitude_data = self.recover_data("ATTITUDE")[0]
        throttle_data = self.recover_data("VFR_HUD")[0]

        if attitude_data is not None and throttle_data is not None:
            roll = attitude_data["roll"] + droll

            if roll_limit is not None:
                roll = np.clip(roll, roll_limit[0], roll_limit[1])

            pitch = attitude_data["pitch"] + dpitch

            if pitch_limit is not None:
                pitch = np.clip(pitch, pitch_limit[0], pitch_limit[1])

            if throttle_limit is not None:
                dthrottle = np.clip(dthrottle, throttle_limit[0], throttle_limit[1])

            if speed_limit is not None:
                if throttle_data["airspeed"] > speed_limit:
                    dthrottle = throttle_data["throttle"]/100 - 0.01

            self.set_attitude(roll, pitch, attitude_data["yaw"] + dyaw, dthrottle)

        else:
            self.send_msg("Failed to get attitude data")

    def request_message_interval(self, message_id: int, frequency_hz: float):
        """
        Request MAVLink message in a desired frequency,
        documentation for SET_MESSAGE_INTERVAL:
            https://mavlink.io/en/messages/common.html#MAV_CMD_SET_MESSAGE_INTERVAL

        Args:
            message_id (int): MAVLink message ID
            frequency_hz (float): Desired frequency in Hz
        """
        self._mavlink.mav.command_long_send(
            self._mavlink.target_system, self._mavlink.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
            message_id,  # The MAVLink message ID
            1e6 / frequency_hz,
            # The interval between two messages in microseconds. Set to -1 to disable and 0 to request default rate.
            0, 0, 0, 0,  # Unused parameters
            0,
            # Target address of message stream (if message has target address fields). 0: Flight-stack default (recommended), 1: address of requestor, 2: broadcast.
        )

    def recover_data(self, request_type) -> tuple[dict, bool]:

        # FIXME: Consider asynchronous receiving
        response = self._mavlink.recv_match(type=request_type)

        if response is not None:
            self._data[request_type] = response.to_dict()
            return response.to_dict(), True

        if request_type in self._data.keys():
            return self._data[request_type], False

        time.sleep(0.01)

        return self.recover_data(request_type)

    def send_msg(self, txt: str, severity: int = 4):
        self._mavlink.mav.statustext_send(severity, txt.encode())

    def send_float(self, name: str, val: float):
        self._mavlink.mav.named_value_float_send(int(1e3 * (time.time() - self.boot_time)),
                                                 name.encode(),
                                                 val)
    def send_int(self, name: str, val: int):
        self._mavlink.mav.named_value_int_send(int(1e3 * (time.time() - self.boot_time)),
                                               name.encode(),
                                               int(val))
