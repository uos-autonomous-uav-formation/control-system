from src.flightsim import *
import numpy as np

sim = Simulator()

for i in [DREFs.elevator_angle, DREFs.AoA, DREFs.yoke_roll, DREFs.yoke_yaw, DREFs.TAS, DREFs.right_aileron,
          DREFs.left_aileron, DREFs.lift_force, "sim/flightmodel/misc/h_ind"]:
    sim.addFreqValue(i)

while True:
    sim.update()

    sim.set(DREFs.side_force, 0.0)
    sim.set(DREFs.pitch_moment, 0.3 * L * sim.get(DREFs.yoke_pitch))
    sim.set(DREFs.aero_roll_moment, 0.4 * L * sim.get(DREFs.yoke_roll))
    sim.set(DREFs.aero_yaw_moment, 0.3 * L * sim.get(DREFs.yoke_yaw))
    sim.set(DREFs.lift_force, L)
    sim.set(DREFs.engine_torque + '[0]', 0)
