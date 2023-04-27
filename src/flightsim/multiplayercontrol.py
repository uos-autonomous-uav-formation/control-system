from multiprocessing import Process
import numpy as np
import time
from .drefs import DREFs
from .sim import Simulator
from ..pid import PID

DIST_STEP = 0.01


def _brng_from_vec(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad = lat1 * np.pi / 180
    lat2_rad = lat2 * np.pi / 180
    delta1 = (lat2 - lat1) * np.pi / 180
    delta2 = (lon2 - lon1) * np.pi / 180

    y = np.sin(delta2) * np.cos(lat2_rad)
    x = np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(delta2)

    brng = np.arctan2(y, x) * 180 / np.pi

    return brng + 360 if brng < 0 else brng


class MultiplayerControl(Process):
    max_roll = 20

    def __init__(self, id: int, target_hdg):
        self.id = id
        super().__init__(target=self._control_system)
        self.start()

    def _start(self):
        self._sim = Simulator()

        self._controller_alt = PID(-1, 0, 0, 0)
        self._controller_roll = PID(-1, 0, -0.05, 0)
        self._controller_pitch = PID(-1, 0.3, 0, 0)
        self._controller_yaw = PID(-1, 0, 0, 0)
        self._sim.add_freq_value(DREFs.multiplayer.elev.format(self.id), 60)
        self._sim.add_freq_value(DREFs.multiplayer.opengl_roll.format(self.id), 60)
        self._sim.add_freq_value(DREFs.multiplayer.opengl_pitch.format(self.id), 60)
        self._sim.add_freq_value(DREFs.multiplayer.opengl_hdg.format(self.id), 60)

    def _control_system(self):
        self._start()

        vx = self._sim.get(DREFs.grafics.opengl_vx)
        vz = self._sim.get(DREFs.grafics.opengl_vz)

        old_alt = self._sim.get(DREFs.multiplayer.elev.format(self.id))
        self._controller_alt.target = old_alt

        while True:
            self._sim.update()
            time.sleep(0.01)

            new_alt = self._sim.get(DREFs.multiplayer.elev.format(self.id))
            current_roll = self._sim.get(DREFs.multiplayer.opengl_roll.format(self.id))
            current_hdg = self._sim.get(DREFs.multiplayer.opengl_hdg.format(self.id))
            current_pitch = self._sim.get(DREFs.multiplayer.opengl_pitch.format(self.id))

            self._sim.set(DREFs.multiplayer.opengl_vx.format(self.id), vx)
            self._sim.set(DREFs.multiplayer.opengl_vy.format(self.id), self._controller_alt.controller(new_alt))
            self._sim.set(DREFs.multiplayer.cs_roll.format(self.id), self._controller_roll.controller(current_roll))
            self._sim.set(DREFs.multiplayer.cs_hdg.format(self.id), self._controller_yaw.controller(current_hdg))
            self._sim.set(DREFs.multiplayer.cs_pitch.format(self.id), self._controller_pitch.controller(current_pitch))
            self._sim.set(DREFs.multiplayer.opengl_vz.format(self.id), vz)
