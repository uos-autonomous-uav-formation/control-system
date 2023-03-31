from src.pid import PID


class AircraftController:
    _pitch_pid: PID
    _roll_pid: PID
    _throttle_pid: PID

    def proc(self, nd_x, nd_y, area) -> (float, float, float, float):
        pitch = self._pitch_pid.controller(nd_y)
        roll = self._roll_pid.controller(nd_x)
        throttle = self._roll_pid.controller(area)
        return roll, pitch, 0, throttle

    def set_target(self, x, y, area):
        if y is not None:
            self._pitch_pid.set_target(y)
        if x is not None:
            self._roll_pid.set_target(x)
        if area is not None:
            self._throttle_pid.set_target(area)


class CessnaController(AircraftController):

    def __init__(self):
        super().__init__()
        self._pitch_pid = PID(0.4, 0, 0, 0)
        self._roll_pid = PID(-0.5, 0, 0, 0)
        self._throttle_pid = PID(10, 0, 0, 0.1)
