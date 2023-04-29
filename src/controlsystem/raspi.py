# import numpy as np
# from picamera2 import Picamera2
# from libcamera import Transform
#
#
# picam2 = Picamera2()
# camera_config = picam2.create_still_configuration(main={"size": (1920, 1082)}, transform=Transform(180))
# picam2.configure(camera_config)
# picam2.start()
# 
# # Initial picture takes longer
# _ = picam2.capture_array()
#
# def raspi(loop: Callable[[np.ndarray, Any], np.ndarray], )
#
#     img = picam2.capture_array()
#     loop(img)