import numpy as np
from scipy.optimize import fsolve

def Model(p0):
    U = 18
    b = 1.5 #span (m)
    p1, p2 = [p0-b/2, p0+b/2]
    ind_1 = np.rad2deg(np.arctan(single_lamb2(p1)/U))
    ind_2 = np.rad2deg(np.arctan(single_lamb2(p2)/U))
    diff = ind_1-ind_2
    return (ind_1, ind_2, diff)

def reading_var(v):
    atm_var1 = []
    atm_var2 = []
    
    for i in range(1000):
        #probe1 = np.random.uniform(-1, 1)
        #probe2 = np.random.uniform(-1, 1)
    
        probe1 = np.random.normal(0, v)
        probe2 = np.random.normal(0, v)

        atm_var1.append(probe1)
        atm_var2.append(probe2)

    probe1_mean = np.mean(atm_var1)
    probe1_std = np.std(atm_var1)
    probe2_mean = np.mean(atm_var2)
    probe2_std = np.std(atm_var2)

    return (probe1_std+probe2_std)/2

readings_l = []
readings_r = []
diff = []
def moving_ave(reading_l, reading_r, a_angle, n_mov):
    reading_l = reading_l - a_angle #input stream of left probe
    reading_r = reading_r - a_angle #input stream of right probe
    
    readings_l.append(reading_l)
    length1 = len(readings_l)
    ave_l = sum(readings_l)/length1
    
    readings_r.append(reading_r)
    length2 = len(readings_r)
    ave_r = sum(readings_r)/length2
    #print(readings_r)
    
    pdiff = ave_l-ave_r
    diff.append(pdiff)
    length5 = len(diff)
    diff_ave = sum(diff)/length5 
    if length1 == n_mov:        
        readings_l.pop(0)
    if length2 == n_mov:
        readings_r.pop(0)
    if length5 == n_mov:
        diff.pop(0)
    return ave_l, ave_r, diff_ave

statelist = []     
def state_est(ave_l, ave_r, diff_ave, reading_std):
    statelist = [] 
    if -(reading_std/2)<diff_ave<(reading_std/2) and -(reading_std/2)<ave_l<(reading_std/2) and -(reading_std/2)<ave_r<(reading_std/2): #to determine constraints if too far
        state = 1
    elif diff_ave>(reading_std/2) and ave_l>(reading_std/2) and ave_r>0.1:
        state = 2
    elif diff_ave<-(reading_std/2) and ave_l<-(reading_std/2) and ave_r>ave_l:
        state = 3
    else:
        state = 4
    statelist.append(state)
    return statelist

def single_lamb2(x):
    y=0
    bm=1.5
    core=0.02
    U = 18
    W = 2.816*9.81
    gamma_0 = -1.1*(4/(np.pi*1.225*U)*(W/bm))
    
    x0, y0 = 0.75, 0 #Vortex position
    r,theta = np.sqrt((x-x0)**2+(y-y0)**2),np.arctan2(y-y0,x-x0) # polar coords
    r_c=core*bm
    
    V_theta = (gamma_0/(2*np.pi*r))*(1-np.exp(-1.26*(r/r_c)**2)) #Lamb-Oseen -1.26
    Vx,Vy = V_theta*np.sin(theta),-V_theta*np.cos(theta) # convert to cartesian again
    V_theta = (Vx**2+Vy**2)**0.5
    return Vy

def Modell(p0, off):
    b = 1.5 #span (m)
    U = 18
    p1 = p0-b/2
    ind_1 = np.rad2deg(np.arctan(single_lamb2(p1)/U))

    return (ind_1-off)

def prob_loc1(ind_1):
    b=1.5
    a1 = fsolve(Modell, 10, args=ind_1)[0]
    p1 = a1-b/2
    return p1

def state_count(statelist):
    state_array = np.zeros(4)
    s1 =statelist.count(1)
    s2 =statelist.count(2)
    s3 =statelist.count(3)
    s4 =statelist.count(4)
    state_array[0] = s1
    state_array[1] = s2
    state_array[2] = s3
    state_array[3] = s4
    return state_array

def state_iden(state_array, target_yaw, ave_l, ideal_span_sep):
    if state_array[0]>state_array[1] and state_array[0]>state_array[2] and state_array[0]>state_array[3]:
        print('State 1')
        if target_yaw <= 12:
            target_yaw = 12
        else:
            target_yaw = target_yaw - 0.01

    if state_array[1]>state_array[0] and state_array[1]>state_array[2] and state_array[1]>state_array[3]:
        print('State 2')
        loc1 = prob_loc1(ave_l)
        print('position estimate', loc1+0.75)
        if (loc1+0.75)>ideal_span_sep:
            if target_yaw <= 12:
                target_yaw = 12
            else:
                target_yaw = target_yaw - 0.005
        if (loc1+0.75)<ideal_span_sep:
            if target_yaw <= 15:
                target_yaw = 15
            else:
                target_yaw = target_yaw + 0.005
        
    if state_array[2]>state_array[0] and state_array[2]>state_array[1] and state_array[2]>state_array[3]:
        print('State 3')
        if target_yaw >= 15:
            target_yaw = 15
        else:
            target_yaw = target_yaw + 0.01
    
    if state_array[3]>state_array[1] and state_array[1]>state_array[0] and state_array[1]>state_array[2]:
        print('State 4')
        if target_yaw > 14.5:
            target_yaw = target_yaw -0.005
        if target_yaw < 14.5:
            target_yaw = target_yaw +0.005
    print(state_array)
    #end = time.time()
    #print('time taken =',f'{end-start:.3}','s')
    #print('modelled position =', f'{pos}', 'm')
    print('Target Yaw =', f'{target_yaw}','˚')

        
    return target_yaw
        