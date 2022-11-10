from src.flightsim import *

sim = Simulator()

DEBUG = []

# while True:
a = cone_leadergen(sim, 1, min_distance=10, max_distance=100, angle=10).load_leader()
a.join()
