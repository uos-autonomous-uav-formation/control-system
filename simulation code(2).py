import numpy as np
from pymavlink import mavutil
from src.computervision import ObjectDetection, liveframe, MODEL_WEIGTS_DIR_CESSNA
from src.controlsystem import dist_from_width, angle_from_xoff, xoff_from_angle
from src.flightsim import *
from src.mavlink import MavlinkConn, SIMULATOR_ADDRS

from src.vortex.Vortex import *
from src.vortex.Vortex_Sim import *
import cv2

import time

TARGET_DIST = 6
TARGET_YAW = 13
TARGET_PITCH = 0
pos=10
atm_var1 = [1]
atm_var2 = [1]
reading_std = 0.5

def wait_heartbeat(m):
    """wait for a heartbeat so we know the target system IDs"""
    print("Waiting for APM heartbeat")

    print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_component))


# NOTE THIS IF IS MANDATORY!!!!! REMOVING IT WILL BREAK PARALELISM
if __name__ == '__main__':
    boot_time = time.time()
    i=0
    # TODO: Start with the initial conditions when engaded

    sim = Simulator()
    sim_process = cone_leadergen(sim, 1, min_distance=3, max_distance=5, angle=0.2).load_leader()

    mavlink = MavlinkConn(SIMULATOR_ADDRS)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 30)
    mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 30)
        
    cv = ObjectDetection(MODEL_WEIGTS_DIR_CESSNA)
    sim = Simulator()
    sim.add_freq_value(DREFs.multiplayer.lon, 60)
    sim.add_freq_value(DREFs.long, 60)
    sim.add_freq_value(DREFs.multiplayer.lat, 60)
    sim.add_freq_value(DREFs.lat, 60)
    
    def loop(img: np.ndarray) -> np.ndarray:
        TARGET_YAW = 13
        global pitch, roll, mavlink

        leaders = cv.process(img)

        cv2.circle(img, center=(int(img.shape[1] * xoff_from_angle(TARGET_YAW)), int(img.shape[0] * xoff_from_angle(TARGET_PITCH))), radius=10, color=(255, 0, 0), thickness=1)
        aprox_dist = 100 
        if len(leaders) > 0:
            aprox_dist = dist_from_width(leaders[0].width_non_dimensional)
            dyaw_angle = angle_from_xoff(leaders[0].center_x_non_dimensional)
            dpitch_angle = angle_from_xoff(leaders[0].center_y_non_dimensional)
            print('aprox dist =', aprox_dist)
            pitch = dpitch_angle - TARGET_PITCH
            roll = 2 * (TARGET_YAW - dyaw_angle)
            throttle = 0.018 * (aprox_dist - TARGET_DIST)

            mavlink.send_float("MAV_CVCONF", leaders[0].confidence * 100)

            with open("flight.csv", "a") as f:
                f.write(f"{aprox_dist},{dyaw_angle},{dpitch_angle},{pitch},{roll},{throttle},{leaders[0].confidence}\n")

            img = leaders[0].render(img)

            mavlink.set_change_in_attitude(roll, pitch, 0, throttle, roll_limit=(-15, 10))

        # TODO: If on guided mode but don't detect leader for a long time switch flight mode to a safe one
        
        
        # Aerodynamic Model -> Set follower on true heading of 0
        # Aerodynamic Control
        n_mov = 10 #Moving average points
        reading_std = 0.5
        ideal_span_sep = 1.6
        pos =10
        i1 = 0
        
        if 80>aprox_dist>25: #and attitude 0?
            if len(atm_var1)>=500 and len(atm_var2)>=500:
                print(1)
                probe1_mean = np.mean(atm_var1)
                print(probe1_mean)
                probe1_std = np.std(atm_var1)
                probe2_mean = np.mean(atm_var2)
                probe2_std = np.std(atm_var2)
                reading_std = (probe1_std+probe2_std)/2
                print('probe1 std =', probe1_std)
                print('probe2 std =', probe2_std)
                print('reading std =', reading_std)
                for i1 in range(50):
                    atm_var1.pop(0)
                    atm_var2.pop(0)
                if reading_std > 1.6:
                    atm_var1.clear()
                    atm_var2.clear()
            else:
                for i in range(50):
                    #start = time.time()
                    sim.update()
                    latf = sim.get(DREFs.lat)
                    longf = sim.get(DREFs.long)
                    latl = sim.get(DREFs.multiplayer.lat)
                    longl = sim.get(DREFs.multiplayer.lon)
                    xl, yl = get_xy(latl, longl)
                    xf, yf = get_xy(latf, longf)
                    #end=time.time()
                    #print(end-start)
                    xsep = -(xl-xf)*4.4806
                    ysep = (yl-yf)*4.4806
                    #print('Xsep',xsep)
                    #print('Ysep', ysep)
                    Probe1 = np.random.normal(Model1(xsep)[0], 0.5, 1)
                    Probe2 = np.random.normal(Model1(xsep)[1], 0.5, 1)
                    atm_var1.append(Probe1[0])
                    atm_var2.append(Probe2[0])
                    
    
           
            
            
            
        
        #Set up for aircraft on the right side of leader
        #if probe values are suitable
        #while 0<aprox_dist<10: #need something like this on the aircraft version
        if reading_std<1.5 and 0<aprox_dist<10:
            start = time.time()
            state_array = np.zeros(4)
            statelist = []
            
            for i in range(11):
                for i in range(5):
                    
                    #Sim only to generate probe readings
                    sim.update()
                    latf = sim.get(DREFs.lat)
                    longf = sim.get(DREFs.long)
                    latl = sim.get(DREFs.multiplayer.lat)
                    longl = sim.get(DREFs.multiplayer.lon)

                    xl, yl = get_xy(latl, longl)
                    xf, yf = get_xy(latf, longf)
                    xsep = -(xl-xf)*4.4806
                    ysep = (yl-yf)*4.4806
                    #print('Xsep',xsep)
                    #print('Ysep', ysep)
                    Probe1 =Model1(xsep)[0]
                    Probe2 =Model1(xsep)[1]
                    #print('Probe1', Probe1)
                    #print('Probe2', Probe2)
                    start = time.time()

                    
                    #Used on the aircraft
                    a_angle = 0 #Expected attitide of the aircraft 
                    reading_l = np.random.normal(Model1(xsep)[0], 0.5, 1) #input stream of left probe
                    reading_r = np.random.normal(Model1(xsep)[1], 0.5, 1) #input stream of right probe
                    ave_l, ave_r, diff_ave=moving_ave(reading_l, reading_r, a_angle, n_mov)
                    end = time.time()
                    #print(end-start)
                #print('ave_l', ave_l)
                #print('ave_r', ave_r)
                #print('diff_ave', diff_ave)
                if -(reading_std/2)<diff_ave<(reading_std/2) and -(reading_std/2)<ave_l<(reading_std/2) and -(reading_std/2)<ave_r<(reading_std/2): #to determine constraints if too far
                    state = 1
                elif diff_ave>(reading_std/2) and ave_l>(reading_std/2) and ave_r>0.1:
                    state = 2
                elif diff_ave<-(reading_std/2) and ave_l<-(reading_std/2) and ave_r>ave_l:
                    state=3
                else:
                    state = 4
                statelist.append(state)
                #print(statelist)
            state_array=state_count(statelist)
            print(state_array)
            end = time.time()
            TARGET_YAW=state_iden(state_array, TARGET_YAW, ave_l, ideal_span_sep)
        
        if reading_std>1.5 and 0<aprox_dist<10:
            TARGET_YAW = 13 #Predefined base on actual position in the lab
            
        
        return img

    liveframe(loop, left=1920)

    sim_process.join()