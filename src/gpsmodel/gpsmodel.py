#This test tries to take the GPS coordinate value from X-plane and implement a GPS error back into X-plane

from src.flightsim import Simulator, DREFs
import time
import random

sim = Simulator()

def GPSError(sim: Simulator) -> (float, float):
    """ Function gets follower position and adds error

    :param sim: Simulator object
    :return: lat, lon as float
    """
    sim.add_freq_value(DREFs.lat)
    sim.add_freq_value(DREFs.long)

    add_or_sub = random.randint(0,3)
    val_1 = random.randint(0,5)
    val_2 = random.randint(0,5)
    lat_Xplane = sim.get(DREFs.lat) #Xplane lattitude
    long_Xplane = sim.get(DREFs.long) #Longitude extracted from Xplane
    lat_Xplane_5dp = (int(lat_Xplane/0.00001))/100000 # Take 5dp of Xplane Latt without rounding up
    long_Xplane_5dp = (int(long_Xplane/0.00001))/100000  # Take 5dp of Xplane Long without rounding up
    lat_Xplane_3dp = (int(lat_Xplane/0.001))/1000   # Take 3dp of Xplane Latt without rounding up
    long_Xplane_3dp = (int(long_Xplane/0.001))/1000  # Take 3dp of Xplane Long without rounding up
    #Getting the last 2 digit of the 5dp coordinate
    lat_Xplane_5dp_l2d = int(str(lat_Xplane_5dp)[-2:])
    long_Xplane_5dp_l2d = int(str(long_Xplane_5dp)[-2:])
    # If value of add_or_sub = 0 take addition of error and last two diggit of 5dp latt@long
    if (add_or_sub) == 0:
        lat_new_l2d = (lat_Xplane_5dp_l2d + val_1)
        long_new_l2d = (long_Xplane_5dp_l2d + val_2)
    elif (add_or_sub) == 1:
        lat_new_l2d = (lat_Xplane_5dp_l2d - val_1)
        long_new_l2d = (long_Xplane_5dp_l2d - val_2)
    elif (add_or_sub) == 2:
        lat_new_l2d = (lat_Xplane_5dp_l2d + val_1)
        long_new_l2d = (long_Xplane_5dp_l2d - val_2)
    else:
        lat_new_l2d = (lat_Xplane_5dp_l2d - val_1)
        long_new_l2d = (long_Xplane_5dp_l2d + val_2)

    lat_error = float(str(lat_Xplane_3dp) + str(lat_new_l2d))
    long_error = float(str(long_Xplane_3dp) + str(long_new_l2d))
    return lat_error, long_error

