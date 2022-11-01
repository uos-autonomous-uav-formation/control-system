from mss import mss
import cv2
from PIL import Image
import numpy as np
from time import time





def grabscreen():
    mon = {'top': 0, 'left': 0, 'width': 1512, 'height': 982} #Screen Size

    sct = mss()
    begin_time = time()
    sct_img = sct.grab(mon)
    print(f"Screen Grab {time() - begin_time}")
    img = Image.frombytes('RGB', (sct_img.size.width, sct_img.size.height), sct_img.rgb)
    print(f"#1 {time() - begin_time}")
    img_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    print(f"#2 {time() - begin_time}")
    cv2.imshow('test', np.array(img_bgr))
    print('This frame takes {} seconds.'.format(time() - begin_time))
    if cv2.waitKey(25) & 0xFF == ord('q'):
       cv2.destroyAllWindows()
       return False
    return True

while True:
    if grabscreen():
        exit(1)