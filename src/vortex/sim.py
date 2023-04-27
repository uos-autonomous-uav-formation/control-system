from src.flightsim import DREFs
from .Vortex_Sim import *
import time


def model(sim):
    sim.update()
    latf = sim.get(DREFs.lat),
    longf = sim.get(DREFs.long)
    latl = sim.get(DREFs.multiplayer.lat)
    longl = sim.get(DREFs.multiplayer.lon)

    xl, yl = get_xy(latl, longl)
    xf, yf = get_xy(latf[0], longf)
    xsep = -(xl-xf)*4.4806
    ysep = (yl-yf)*4.4806
    pitch1 =np.random.normal(Model1(xsep)[0], 0.2, 1)
    pitch2 =np.random.normal(Model1(xsep)[1], 0.2, 1)
    return pitch1, pitch2

