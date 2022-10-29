from src.flightsim import Simulator, DREFs
import time
from src.gpsmodel import GPSError

sim = Simulator()

a, b = GPSError(sim)

print(a)
print(b)

sim.set(DREFs.lat, a)
sim.set(DREFs.long, b)
