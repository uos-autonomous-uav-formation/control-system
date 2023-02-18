import cv2
import numpy as np
from math import floor


def objectdetection_video(videoname):
    # net = cv2.dnn.readNet('yolov4-tiny.weights', 'yolo4-tiny.cfg')
    # net = cv2.dnn.readNet('yolov4-tiny.cfg', 'yolov4-tiny.weights')
    net = cv2.dnn.readNet('yolov4-tiny-custom-2.cfg', 'yolov4-tiny-custom_best-3.weights')
    # net = cv2.dnn.readNet('yolov4.cfg', 'yolov4.weights')

    classes = []
    with open("../models/classes.txt", "r") as f:
        classes = f.read().splitlines()

    cap = cv2.VideoCapture(videoname)
    font = cv2.FONT_HERSHEY_PLAIN
    # colors = np.random.uniform(0, 255, size=(100, 3))

    while True:

        _, img = cap.read()
        height, width, _ = img.shape

        blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        net.setInput(blob)
        output_layers_names = net.getUnconnectedOutLayersNames()
        layerOutputs = net.forward(output_layers_names)

        boxes = []
        confidences = []
        class_ids = []

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.25 and class_id == 0:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append((float(confidence)))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.4)

        if len(indexes) > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                confidence = str(round(confidences[i], 2))
                color = (0, 255, 0)  # colors[i]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label + " " + confidence, (x, y + 20), font, 2, (255, 255, 255), 2)

        cv2.imshow('Image', img)
        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def imageobject(imagename):
    net = cv2.dnn.readNet('src\\ComputerVision\\yolov4-tiny-custom-2.cfg',
                          'src\\ComputerVision\\yolov4-tiny-custom_best-3.weights')

    classes = []
    with open("src\\ComputerVision\\classes.txt", "r") as f:
        classes = f.read().splitlines()

    img = cv2.imread(imagename)
    img = cv2.resize(img, (500, 1080))
    height, width, _ = img.shape

    blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
    # blob = cv2.dnn.blobFromImage(img, 1, (floor(height/32) * 32, floor(width/32) * 32), (0, 0, 0), swapRB=True, crop=False)

    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)

    boxes = []
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.1 and class_id == 0:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.1, 0.4)

    font = cv2.FONT_HERSHEY_PLAIN

    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            color = (0, 255, 0)  # colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label + " " + confidence, (x, y + 20), font, 2, (255, 255, 255), 2)

    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def testing(imagename):
    # net = cv2.dnn.readNet('yolov3.cfg', 'yolo3.weights')
    # net = cv2.dnn.readNet('yolov3-tiny_testing.cfg','yolov3-tiny_training_last.weights')
    # net = cv2.dnn.readNet('yolo3-tiny.cfg', 'yolov3-tiny.weights')
    # net = cv2.dnn.readNet('yolov4-tiny.cfg', 'yolov4-tiny.weights')
    net = cv2.dnn.readNet('yolov4-tiny-custom-2.cfg', 'yolov4-tiny-custom_best-3.weights')
    # net = cv2.dnn.readNet('yolov4.cfg', 'yolov4.weights')
    # net = cv2.dnn.readNet('yolov4-tiny(3class).cfg', 'yolov4-tiny(3class).weights')

    classes = []
    with open("../models/classes.txt", "r") as f:
        classes = f.read().splitlines()

    img = cv2.imread(imagename)
    height, width, _ = img.shape

    blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)

    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)

    boxes = []
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.01 and class_id == 0:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.01, 0.4)

    font = cv2.FONT_HERSHEY_PLAIN

    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            color = (0, 255, 0)  # colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label + " " + confidence, (x, y + 20), font, 2, (255, 255, 255), 2)

        cv2.imshow('Image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# objectdetection_video("110.MP4")
# testing("13.jpg")
