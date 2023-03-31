from pymavlink import mavutil
from pymavlink.quaternion import QuaternionBase
from datetime import datetime
import time
import math


class MavlinkConn:
    last_heartbeat: datetime
    boot_time: float
    _data: dict[str, dict] = {}

    def __init__(self, device: str, ):
        self._mavlink = mavutil.mavlink_connection(device, baud=57600, source_system=255)
        self.boot_time = time.time()

    def _heartbeat(self, blocking: bool = False) -> bool:
        msg = self._mavlink.recv_match(type='HEARTBEAT', blocking=blocking)

        # TODO: Check validity of heart beat
        # TODO: Handle lack of heartbeats in other commands
        # TODO: Send own heartbeat at a frequency

    def set_attitude(self, roll, pitch, yaw, throttle):
        self._mavlink.mav.set_attitude_target_send(
            int(1e3 * (time.time() - self.boot_time)),  # ms since boot
            self._mavlink.target_system, self._mavlink.target_component,
            mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_BODY_YAW_RATE_IGNORE,
            # -> attitude quaternion (w, x, y, z | zero-rotation is 1, 0, 0, 0)
            QuaternionBase([math.radians(angle) for angle in (roll, pitch, yaw)]),
            0, 0, 0, throttle  # roll rate, pitch rate, yaw rate, thrust
        )

    def set_change_in_attitude(self, droll, dpitch, dyaw, dthrottle):
        attitude_data = self.recover_data("ATTITUDE")
        throttle_data = self.recover_data("VFR_HUD")

        if attitude_data is not None and throttle_data is not None:
            self.set_attitude(attitude_data["roll"] + droll, attitude_data["pitch"] + dpitch, attitude_data["yaw"] + dyaw, throttle_data["throttle"] + dthrottle)

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

    def recover_data(self, request_type) -> dict:

        # FIXME: Consider asynchronous receiving
        response = self._mavlink.recv_match(type=request_type)

        if response is not None:
            self._data[request_type] = response.to_dict()
            return response.to_dict()

        if request_type in self._data.keys():
            return self._data[request_type]