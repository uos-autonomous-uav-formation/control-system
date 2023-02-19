import cv2
import numpy as np
import time
from . import MODEL_CFG_DIR, MODEL_WEIGTS_DIR, CLASSES
from dataclasses import dataclass


def load_img_from_file(filename: str):
    return cv2.imread(filename)


@dataclass
# FIXME: Python dataclasses in Python 3.9 are not as optimum. Reconsider structure and storage of this information
class Leader:
    _scores: np.ndarray[float]
    class_id: int
    confidence: float
    center_x_non_dimensional: float
    center_y_non_dimensional: float
    center_x: float
    center_y: float
    width_non_dimensional: float
    height_non_dimensional: float
    width: float
    height: float

    def __init__(self, detection: np.ndarray[float], width: int, height: int):
        self._scores = detection[5:]
        self.class_id = np.argmax(self._scores)
        self.confidence = self._scores[self.class_id]

        self.center_x_non_dimensional = detection[0]
        self.center_x = self.center_x_non_dimensional * width

        self.center_y_non_dimensional = detection[1]
        self.center_y = detection[1] * height

        self.width_non_dimensional = detection[2]
        self.width = self.width_non_dimensional * width

        self.height_non_dimensional = detection[3]
        self.height = detection[3] * height

    def top(self):
        return int(self.center_y - self.height / 2)

    def bottom(self):
        return int(self.center_y + self.height / 2)

    def left(self):
        return int(self.center_x - self.width / 2)

    def right(self):
        return int(self.center_x + self.width / 2)

    def render(self, img: np.ndarray) -> np.ndarray:
        label = str(CLASSES[self.class_id])
        confidence = str(round(self.confidence, 2))
        color = (0, 255, 0)

        cv2.rectangle(img, (self.left(), self.top()), (self.right(), self.bottom()), color, 2)
        cv2.putText(img, label + " " + confidence, (int(self.center_x), int(self.center_y)), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 255, 255), 2)

        return img


class ObjectDetection:
    __net: cv2.dnn.Net

    def __init__(self):
        self._load_net()

    def _load_net(self) -> None:
        self.__net = cv2.dnn.readNet(MODEL_CFG_DIR, MODEL_WEIGTS_DIR)

    def process(self, img: np.ndarray) -> list[Leader]:
        height, width, _ = img.shape

        start = time.time()

        blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        self.__net.setInput(blob)

        layer_output = self.__net.forward(self.__net.getUnconnectedOutLayersNames())

        leader_box: list[Leader] = []

        for output in layer_output:
            output = output[output[:, 5] > 0.1]
            for detection in output:
                leader_box.append(Leader(detection, width, height))

        print(time.time() - start)

        return leader_box

    def render(self, img: np.ndarray) -> np.ndarray:
        for i in self.process(img):
            i.render(img)

        return img
