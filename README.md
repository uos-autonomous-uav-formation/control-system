# Formation flight UAV control system

Currently based on computer vision and GPS


# DREF information


https://developer.x-plane.com/datarefs/


```python

from src.flightsim import Simulator, DREFs
import time

sim = Simulator()

sim.add_freq_value(DREFs.lat)
sim.add_freq_value(DREFs.long)


sim.update()

print(sim.get(DREFs.lat), sim.get(DREFs.long))


```