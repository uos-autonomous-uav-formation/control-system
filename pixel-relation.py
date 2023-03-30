import re
import pandas as pd
from src.computervision import load_img_from_file, ObjectDetection, MODEL_WEIGTS_DIR_DRACO
from os import listdir
from os.path import isfile, join
import cv2
import numpy as np

img_dir = "C:\\Users\\alvar\\University of Southampton\\GDP - Control System\\pictures"


def regex(input_comment: str) -> (float, float, float):
    result = re.search(r"d([0-9]+)h([0-9-]+)p([0-9]+)r?([0-9]*).jpg", input_comment)
    return result.group(1), result.group(2), result.group(3), result.group(4)


def post_process(cv: ObjectDetection, filename: str) -> (float, float, float, float):
    img = load_img_from_file(join(img_dir, filename))
    leaders = cv.process(img)

    if len(leaders) > 0:
        leader = leaders[0]

        return leader.confidence, leader.width_non_dimensional, leader.height_non_dimensional, leader.center_x_non_dimensional

    print(f"Failed to find anything in {filename}")
    return None, None, None, None


if __name__ == "__main__":
    cv = ObjectDetection(MODEL_WEIGTS_DIR_DRACO)

    # Get all file names of images
    files = [f for f in listdir(img_dir) if isfile(join(img_dir, f))]

    # Remove the file names that don't match the structure
    condition = re.compile(r'd[0-9]+h[0-9-]+p[0-9]+r?[0-9]*.jpg')
    img = [s for s in files if condition.match(s)]

    # Load the filenames into Pandas dataframe
    data = pd.DataFrame()

    data["filename"] = img

    data["distance"], data["yaw"], data["pitch"], data["resolution"] = zip(*data["filename"].map(regex))

    # Iterate over pandas dataframe to determine the values of pixels with respect to angles and distances
    data["confidence"], data["width_nd"], data["height_nd"], data["center_x_nd"] = zip(*data["filename"].map(lambda x: post_process(cv, x)))

    data.to_csv("output.csv")
