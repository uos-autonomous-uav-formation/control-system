MODEL_CFG_DIR = "src\\ComputerVision\\models\\yolov4-tiny-custom-2.cfg"
MODEL_WEIGTS_DIR_DRACO = "src\\ComputerVision\\models\\yolov4-27march.weights"
MODEL_WEIGTS_DIR_CESSNA = "src\\ComputerVision\\models\\yolov4-tiny-c172.weights"

with open("src\\ComputerVision\\models\\classes.txt", "r") as f:
    CLASSES = f.readlines()

from .screen import grab_screen_frame, liveframe
from .objectdetection import ObjectDetection, load_img_from_file
