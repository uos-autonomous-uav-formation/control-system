from pymavlink import mavutil
from datetime import datetime


class MavlinkConn:
    last_heartbeat: datetime

    def __init__(self, device: str, ):
        self._mavlink = mavutil.mavlink_connection(device, baud=57600, source_system=255)

    def _heartbeat(self, blocking: bool = False) -> bool:
        msg = self._mavlink.recv_match(type='HEARTBEAT', blocking=blocking)

        # TODO: Check validity of heart beat
        # TODO: Handle lack of heartbeats in other commands
