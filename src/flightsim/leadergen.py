__author__ = "Alvaro Sierra Castro"
__version__ = "0.1.0"  # Using https://semver.org/ standard
__maintainer__ = "Alvaro Sierra Castro"
__credits__ = []
__email__ = "asc1g19@soton.ac.uk"
__status__ = "Prototyping"

from dataclasses import dataclass
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
    _simv: Simulator = None

    # TODO: Handle this arcraft data not being filled in (and either generate or raise error)
    _flw: _aircraft = None
    _ldr_id: int = None

    def __init__(self, simulator: Simulator, acft_id: int):
        self._simv = simulator
        self._ldr_id = acft_id

        self._get_flw_pos()

    def load_leader(self, y_delta: float = 0):
        self._gen_leader(self._flw, y_delta)
        self._create_multiplayer_control(self._flw)

    def _gen_leader(self, aircraft: _aircraft, y_delta) -> None:
        # Y is height, Z is north, X is east (units not the same)
        self._sim.set(f"sim/operation/override/override_autopilot[{self._ldr_id}]", True)

        self._sim.set(DREFs.multiplayer.opengl_hdg.format(self._ldr_id), aircraft.hdg)
        self._sim.set(DREFs.multiplayer.opengl_pitch.format(self._ldr_id), aircraft.pitch)
        self._sim.set(DREFs.multiplayer.opengl_roll.format(self._ldr_id), aircraft.roll)
        self._sim.set(DREFs.multiplayer.opengl_vx.format(self._ldr_id), aircraft.vx)
        self._sim.set(DREFs.multiplayer.opengl_vy.format(self._ldr_id), aircraft.vy)
        self._sim.set(DREFs.multiplayer.opengl_vz.format(self._ldr_id), aircraft.vz)
        self._sim.set(DREFs.multiplayer.opengl_x.format(self._ldr_id), aircraft.x)
        self._sim.set(DREFs.multiplayer.opengl_y.format(self._ldr_id), aircraft.y + y_delta)
        self._sim.set(DREFs.multiplayer.opengl_z.format(self._ldr_id), aircraft.z)
        self._sim.set(DREFs.multiplayer.cs_pitch.format(self._ldr_id), aircraft.cs_pitch)
        self._sim.set(DREFs.multiplayer.cs_roll.format(self._ldr_id), aircraft.cs_roll)
        self._sim.set(DREFs.multiplayer.cs_hdg.format(self._ldr_id), aircraft.cs_hdg)

        self._sim.set(DREFs.multiplayer.flap.format(self._ldr_id + 1), 0)

    def _create_multiplayer_control(self, target_hdg):
        self.controller = MultiplayerControl(self._sim, self._ldr_id, target_hdg)
        self.controller.join()


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
        # for i in to_flush:
        #     self._sim.add_freq_value(i, 0)


class Cone(_Loader):
    _max: float
    _min: float

    def _get_lead_pos(self):
        pass
