
dist_m = 1.8743677488601618
dist_c = - 0.02772805569491069 / 1.8743677488601618


def dist_from_width(width: float):
    return dist_m / width + dist_c


yaw_m = 1 / - 0.02516941505106
yaw_c = - 0.5363684179915779 / - 0.02516941505106


def angle_from_xoff(nd_x_off: float):
    return yaw_m * nd_x_off + yaw_c


def xoff_from_angle(angle: float):
    return -0.02516941505106 * angle + 0.5363684179915779