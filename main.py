from src.computervision import ObjectDetection, load_img_from_file, liveframe


# NOTE THIS IF IS MANDATORY!!!!! REMOVING IT WILL BREAK PARALELISM
if __name__ == '__main__':
    cv = ObjectDetection()

    liveframe(cv.render)
