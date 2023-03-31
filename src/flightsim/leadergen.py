__author__ = "Alvaro Sierra Castro"
__version__ = "0.1.0"  # Using https://semver.org/ standard
__maintainer__ = "Alvaro Sierra Castro"
__credits__ = []
__email__ = "asc1g19@soton.ac.uk"
__status__ = "Prototyping"

import copy
from dataclasses import dataclass
import random
import numpy as np
from threading import Thread
from . import Simulator, DREFs, MultiplayerControl


@dataclass(init=True)
class _aircraft:
    """
    **For convention store lat, lon, hdg and pitch in rad**
    """
    x: float
    y: float
    z: float
    hdg: float
    pitch: float
    roll:float
    vx: float
    vy: float
    vz: float
    cs_roll: float
    cs_hdg: float
    cs_pitch: float


class _Loader:
    """
    Backbone of all the position generation for leader aircraft
    """

    _simv: Simulator = None

    # TODO: Handle this arcraft data not being filled in (and either generate or raise error)
    _flw: _aircraft = None
    _ldr_id: int = None
    _args = dict = {}

    def __init__(self, simulator: Simulator, acft_id: int, **kwargs):
        self._simv = simulator
        self._ldr_id = acft_id
        self._args = kwargs

        self._get_flw_pos()

    def load_leader(self, y_delta: float = 0) -> Thread:
        """ Load the leader and bind a control system to it

        :rtype: Thread
        :return: Thread running the control of the leader aircraft. Call Thread.join() at the end of
        the code so the main thread waits for this one to *never* finish
        """
        self._gen_leader(self._get_lead_pos())
        return self._create_multiplayer_control(self._flw)

    def _gen_leader(self, aircraft: _aircraft) -> None:
        # Y is height, Z is north, X is east (units not the same)
        # self._sim.set(f"sim/operation/override/override_autopilot[{self._ldr_id}]", True)

        self._sim.set(DREFs.multiplayer.opengl_hdg.format(self._ldr_id), aircraft.hdg)
        self._sim.set(DREFs.multiplayer.opengl_pitch.format(self._ldr_id), aircraft.pitch)
        self._sim.set(DREFs.multiplayer.opengl_roll.format(self._ldr_id), aircraft.roll)
        self._sim.set(DREFs.multiplayer.opengl_vx.format(self._ldr_id), aircraft.vx)
        self._sim.set(DREFs.multiplayer.opengl_vy.format(self._ldr_id), aircraft.vy)
        self._sim.set(DREFs.multiplayer.opengl_vz.format(self._ldr_id), aircraft.vz)
        self._sim.set(DREFs.multiplayer.opengl_x.format(self._ldr_id), aircraft.x)
        self._sim.set(DREFs.multiplayer.opengl_y.format(self._ldr_id), aircraft.y)
        self._sim.set(DREFs.multiplayer.opengl_z.format(self._ldr_id), aircraft.z)
        self._sim.set(DREFs.multiplayer.cs_pitch.format(self._ldr_id), aircraft.cs_pitch)
        self._sim.set(DREFs.multiplayer.cs_roll.format(self._ldr_id), aircraft.cs_roll)
        self._sim.set(DREFs.multiplayer.cs_hdg.format(self._ldr_id), aircraft.cs_hdg)

        self._sim.set(DREFs.multiplayer.flap.format(self._ldr_id + 1), 0)

    def _create_multiplayer_control(self, target_hdg) -> Thread:
        self.controller = MultiplayerControl(self._ldr_id, target_hdg)
        return self.controller

    @property
    def _sim(self):
        if self._simv is None:
            raise TypeError("Simulator not defined")
        else:
            return self._simv

    def _get_flw_pos(self):
        # TODO: For future proofing see https://github.com/uos-autonomous-uav-formation/control-system/issues/3

        req = [DREFs.grafics.opengl_x, DREFs.grafics.opengl_y, DREFs.grafics.opengl_z, DREFs.grafics.opengl_hdg,
               DREFs.grafics.opengl_pitch, DREFs.cs_pitch, DREFs.cs_roll, DREFs.cs_hdg,
               DREFs.grafics.opengl_vx, DREFs.grafics.opengl_vy, DREFs.grafics.opengl_vz]
        to_flush = []
        for i in req:
            if not self._sim.is_dref_recieved(i):
                to_flush.append(i)
                self._sim.add_freq_value(i, 1)

        self._sim.update()

        self._flw = _aircraft(x=self._sim.get(DREFs.grafics.opengl_x),
                              y=self._sim.get(DREFs.grafics.opengl_y),
                              z=self._sim.get(DREFs.grafics.opengl_z),
                              hdg=self._sim.get(DREFs.grafics.opengl_hdg),
                              pitch=self._sim.get(DREFs.grafics.opengl_pitch),
                              roll=self._sim.get(DREFs.grafics.opengl_roll),
                              vx=self._sim.get(DREFs.grafics.opengl_vx),
                              vy=self._sim.get(DREFs.grafics.opengl_vy),
                              vz=self._sim.get(DREFs.grafics.opengl_vz),
                              cs_pitch=self._sim.get(DREFs.cs_pitch),
                              cs_roll=self._sim.get(DREFs.cs_roll),
                              cs_hdg=self._sim.get(DREFs.cs_hdg))

        # Flush the DREFs we initialised (we only need them once)
        for i in to_flush:
            self._sim.add_freq_value(i, 0)

    def _get_lead_pos(self):
        return self._flw


class Cone(_Loader):

    def __init__(self, simulator: Simulator, acft_id: int, **kwargs):
        """
        Generate the leader around a cone shape

        :param simulator: Simulator object to send data and recieve from X-Plane. This will only be used in loading. A second will be used for the separate Thread
        :type simulator: Simulator
        :param acft_id: ID of multiplayer aircraft to use (typically 1)
        :type acft_id: int
        :key max_distance: maximum distance (in opengl coordinates) to spawn the aircraft at
        :type max_distance: int
        :key min_distance: minimum distance (in opengl coordinates) to spawn the aircarft at
        :type min_distance: int
        :key angle: maximum range angle in radians to generate the aircrat for (defaults to 0.7). This will aply in a +- range for that single value
        :type angle: float
        """
        super(Cone, self).__init__(simulator, acft_id, **kwargs)

    def _get_lead_pos(self):
        angle = 0.7 if "angle" not in self._args.keys() else self._args["angle"]

        angle = random.uniform(-angle, angle)
        dist = random.randint(10 if "min_distance" not in self._args.keys() else self._args["min_distance"],
                              100 if "max_distance" not in self._args.keys() else self._args["max_distance"])
        leader = copy.copy(self._flw)

        leader.y = self._flw.y + random.randint(-10, 100)
        leader.x = self._flw.x + dist * (self._flw.vx * np.cos(angle) - self._flw.vz * np.sin(angle))
        leader.z = self._flw.z + dist * (self._flw.vx * np.sin(angle) + self._flw.vz * np.cos(angle))

        return leader
