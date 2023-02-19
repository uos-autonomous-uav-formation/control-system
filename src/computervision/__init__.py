MODEL_CFG_DIR = "src\\ComputerVision\\models\\yolov4-tiny-custom-2.cfg"
MODEL_WEIGTS_DIR = "src\\ComputerVision\\models\\yolov4-tiny-custom_best-3.weights"

with open("src\\ComputerVision\\models\\classes.txt", "r") as f:
    CLASSES = f.readlines()



from .screen import grab_screen_frame, liveframe
from .objectdetection import ObjectDetection, load_img_from_file
