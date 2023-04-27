MODEL_CFG_DIR = "src/computervision/models/yolov4-tiny-custom-2.cfg"
MODEL_WEIGTS_DIR_DRACO = "src/computervision/models/yolov4-27march.weights"
MODEL_WEIGTS_DIR_CESSNA = "src/computervision/models/yolov4-tiny-c172.weights"

with open("src/computervision/models/classes.txt", "r") as f:
    CLASSES = f.readlines()

try:
    from .screen import grab_screen_frame, liveframe

except Exception as e:
    print(f"Failed to load screen recording: {e}")

from .objectdetection import ObjectDetection, load_img_from_file
