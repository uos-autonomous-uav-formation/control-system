from src.flightsim import *

if __name__ == "__main__":
    sim = Simulator()
    sim_process = cone_leadergen(sim, 1, min_distance=5, max_distance=7, angle=0).load_leader()



    sim_process.join()
