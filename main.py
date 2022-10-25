from src.flightsim import Simulator, DREFs
import time

sim = Simulator()

sim.add_freq_value(DREFs.lat)
sim.add_freq_value(DREFs.long)


sim.update()

print(sim.get(DREFs.lat), sim.get(DREFs.long))


