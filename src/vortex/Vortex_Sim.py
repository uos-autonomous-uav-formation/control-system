import numpy as np
from scipy.optimize import fsolve
import math

def Vort_Mod1(x): #x spanwise, y vertical, z downstream
    y=0    
    bm = 1.5
    Ul = 18
    gamma_0 = -(1.35)*(4/(np.pi*1.225*Ul)*(2.82*9.81/bm))
    x0, y0 = 0.61, 0 #Vortex position
    r,theta = np.sqrt((x-x0)**2+(y-y0)**2),np.arctan2(y-y0,x-x0) # polar coords
    r_c=0.02*bm
    
    V_theta = (gamma_0/(2*np.pi*r))*(1-np.exp(-1.26*(r/r_c)**2)) #Lamb-Oseen -1.26
    Vx,Vy = V_theta*np.sin(theta),-V_theta*np.cos(theta) # convert to cartesian again
    V_theta = (Vx**2+Vy**2)**0.5
    return Vy

def Model_l1(x, off):
    Uf = 18
    b = 1.5 #span (m)
    p1 = x-b/2
    ind_1 = np.rad2deg(np.arctan(Vort_Mod1(p1)/Uf))
    return ind_1 - off

def Model_r1(x, off):
    Uf = 18
    b = 1.5 #span (m)
    p2 = x+b/2
    ind_2 = np.rad2deg(np.arctan(Vort_Mod1(p2)/Uf))
    return ind_2 - off

def prob_loc1(ind1, ind2):
    b = 1.5 #span (m)
    a1= fsolve(Model_l1, 10, args=(ind1))
    a2= fsolve(Model_r1, 10, args=(ind2))
    p1 = a1-b/2
    p2 = a1+b/2
    return p1, p2

def Model1(x):
    Uf = 18
    b = 1.5 #span (m)pp
    p1, p2 = [x-b/2, x+b/2]
    ind_1 = np.rad2deg(np.arctan(Vort_Mod1(p1)/Uf))
    ind_2 = np.rad2deg(np.arctan(Vort_Mod1(p2)/Uf))
    diff = ind_1-ind_2
    return (ind_1, ind_2, diff)

def get_xy(lat, lng):
    mapWidth=2058
    mapHeight=1746
    factor=.404
    x_adj=-391
    y_adj=37
    x = (mapWidth*(180+lng)/360)%mapWidth+(mapWidth/2)
    latRad = lat*(math.pi/180)
    mercN = math.log(math.tan((math.pi/4)+(latRad/2)))
    y = (mapHeight/2)-(mapWidth*mercN/(2*math.pi))
    x = x*factor+x_adj
    y = y*factor+y_adj
    return x*1000, y*1000