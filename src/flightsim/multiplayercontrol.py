import time
from copy import copy
from threading import Thread
import numpy as Math
from .drefs import DREFs
from .sim import Simulator
from time import sleep

DIST_STEP = 0.01


class _PID(object):
    error: float = 0
    integral_error: float = 0
    error_last: float = 0
    output: float = 0

    def __init__(self, kp: float, ki: float, kd: float, target: float):
        self.kp: float = kp
        self.ki: float = ki
        self.kd: float = kd
        self.target: float = target

    def controller(self, pos: float) -> float:
        self.error = pos - self.target

        self.integral_error += self.error * DIST_STEP
        derivative_error = (self.error - self.error_last) / DIST_STEP
        self.output = self.kp * self.error + self.ki*self.integral_error + self.kd * derivative_error
        self.error_last = copy(self.error)

        return self.output


def _brng_from_vec(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad = lat1 * Math.pi / 180
    lat2_rad = lat2 * Math.pi / 180
    delta1 = (lat2 - lat1) * Math.pi / 180
    delta2 = (lon2 - lon1) * Math.pi / 180

    y = Math.sin(delta2) * Math.cos(lat2_rad)
    x = Math.cos(lat1_rad) * Math.sin(lat2_rad) - Math.sin(lat1_rad) * Math.cos(lat2_rad) * Math.cos(delta2)

    brng = Math.arctan2(y, x) * 180 / Math.pi

    return brng + 360 if brng < 0 else brng


class MultiplayerControl(Thread):
    max_roll = 20

    def __init__(self, sim: Simulator, id: int, target_hdg):
        self.id = id
        self._sim: Simulator = sim

        self._controller_alt = _PID(-1, 0, 0, 0)
        self._controller_roll = _PID(-1, 0, 0, 0)
        self._controller_pitch = _PID(-1, 0, 0, 0)
        self._controller_yaw = _PID(-1, 0, 0, 0)
        self._sim.add_freq_value(DREFs.multiplayer.elev.format(self.id), 60)
        self._sim.add_freq_value(DREFs.multiplayer.opengl_roll.format(self.id), 60)
        self._sim.add_freq_value(DREFs.multiplayer.opengl_pitch.format(self.id), 60)
        self._sim.add_freq_value(DREFs.multiplayer.opengl_hdg.format(self.id), 60)

        super().__init__(target=self._control_system)

        self.start()

    def _control_system(self):
        vx = self._sim.get(DREFs.grafics.opengl_vx)
        vz = self._sim.get(DREFs.grafics.opengl_vz)

        old_alt = self._sim.get(DREFs.multiplayer.elev.format(self.id))
        self._controller_alt.target = old_alt

        while True:
            self._sim.update()

            new_alt = self._sim.get(DREFs.multiplayer.elev.format(self.id))
            current_roll = self._sim.get(DREFs.multiplayer.opengl_roll.format(self.id))
            current_hdg = self._sim.get(DREFs.multiplayer.opengl_hdg.format(self.id))
            current_pitch = self._sim.get(DREFs.multiplayer.opengl_pitch.format(self.id))

            print(f"{current_pitch=}, {current_hdg=}, {current_roll=}")

            self._sim.set(DREFs.multiplayer.opengl_vx.format(self.id), vx)
            self._sim.set(DREFs.multiplayer.opengl_vy.format(self.id), self._controller_alt.controller(new_alt))
            self._sim.set(DREFs.multiplayer.cs_roll.format(self.id), self._controller_roll.controller(current_roll))
            self._sim.set(DREFs.multiplayer.cs_hdg.format(self.id), self._controller_yaw.controller(current_hdg))
            self._sim.set(DREFs.multiplayer.cs_pitch.format(self.id), self._controller_pitch.controller(current_pitch))
            self._sim.set(DREFs.multiplayer.opengl_vz.format(self.id), vz)

            # time.sleep(0.01)
