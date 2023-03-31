import time
from copy import copy


class PID(object):
    error: float = 0
    integral_error: float = 0
    error_last: float = 0
    output: float = 0

    def __init__(self, kp: float, ki: float, kd: float, target: float):
        self.kp: float = kp
        self.ki: float = ki
        self.kd: float = kd
        self.target: float = target
        self._previous_time = time.time() - 20

    def set_target(self, new_target: float):
        self.target = new_target

    def controller(self, pos: float) -> float:
        current_time = time.time()

        self.error = pos - self.target

        self.integral_error += self.error * (current_time - self._previous_time)
        derivative_error = (self.error - self.error_last) / (current_time - self._previous_time)
        self.output = self.kp * self.error + self.ki*self.integral_error + self.kd * derivative_error

        self.error_last = copy(self.error)
        self._previous_time = current_time

        return self.output
