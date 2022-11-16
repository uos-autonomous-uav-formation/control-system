from src.ComputerVision import CameraVision, ObjectDetection


# NOTE THIS IF IS MANDATORY!!!!! REMOVING IT WILL BREAK PARALELISM
if __name__ == '__main__':
    ObjectDetection.objectdetection_video(CameraVision.livecamera())