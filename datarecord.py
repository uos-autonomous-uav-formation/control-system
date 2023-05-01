from picamera2 import Picamera2
from libcamera import Transform
from src.mavlink import MavlinkConn, RASPI
from src.aoa_sensor import *
from pymavlink import mavutil
import time
import busio
import board
from datetime import datetime


def take_picture(filename: str, camera: Picamera2):
    return camera.capture_file(f"images/{filename}.jpg", wait=False)

def print2(text: str):
    text = f"{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}: {text}"
    print(text)
    with open("errorlog.txt", "a") as f:
        f.write(text + "\n")



def mavlink_picture(mavlink: MavlinkConn, camera: Picamera2):
    try:
        return take_picture(f"t{time.time()}c{mavlink.corrected_timestamp()}", camera)
    except Exception as e:
        print2(f"Error recording ps with Mavlink at {e}")

        return take_picture(f"t{time.time()}", camera)


def log_ps(command: str, aoa_sensors: list[AoaSensor]):
    # TODO: Restructure the csv 
    with open("ps_data.csv", "a") as file:
        for aoa_sensor in aoa_sensors:
            file.write(f"{command},{aoa_sensor.id},0" + 
                        ",".join([f"{aoa_sensor.pressure_sensor_dvoltage(i)},{aoa_sensor.pressure_sensor_zero(i)}" for i in [1, 2, 3, 4, 5]]) + 
                        f",\n")


def mavlink_ps(mavlink: MavlinkConn, aoa_sensor: AoaSensor):
    try:
        log_ps(f"t{time.time()}c{mavlink.corrected_timestamp()}", aoa_sensor)
    except Exception as e:
        print2(f"Error recording ps with Mavlink at {e}")

        log_ps(f"t{time.time()}")



if __name__ == '__main__':
    resolution = (1920,1080)

    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={"size": resolution}, transform=Transform(180))
    picam2.configure(camera_config)
    picam2.start()
    time.sleep(1)
    print2("Camera initiated")

    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    aoa_2 = AoaSensor(2, spi, board.D20, 5, AoA2_conf)
    aoa_1 = AoaSensor(1, spi, board.D7, 5, AoA1_conf)
    print2("Pressure sensor initiated")

    try:
        mavlink = MavlinkConn(RASPI)
        mavlink.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_SYSTEM_TIME, 1)
        mavlink.corrected_timestamp()
        print2("Mavlink initiated")

    except Exception as e:
        mavlink = None
        print2("Mavlink failed to initialized. No corrected timestamp will be available")

    while True:
        # TODO: Better structure trys
        start = time.time()
        
        try:
            
            if mavlink == None:
                print2("Looping non mavlink")
                job = take_picture(f"t{time.time()}", picam2)

                for _ in range(0, 15):
                    log_ps(f"t{time.time()}", [aoa_1, aoa_2])                

                picam2.wait(job)
                print2(f"Completed solo {time.time() - start}")
                
            else:
                print2("Looping mavlink")
                job = mavlink_picture(mavlink, picam2)
                for _ in range(0, 15):
                    mavlink_ps(mavlink, [aoa_1, aoa_2])

                picam2.wait(job)
                print2(f"Completed mavlink {time.time() - start}")

        except Exception as e:
            print2(f"Error cascaded to external handler {e}")
