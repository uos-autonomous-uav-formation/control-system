from mss.base import MSSBase
from mss import mss
import numpy as np
from typing import Callable, Any
import time
import cv2


def grab_screen_frame(ScreenDriver: MSSBase, top: int = 0, left: int = 0, width: int = 1920,
                      height: int = 1080) -> np.ndarray:
    """ Get a screen frame as a Pillow image.

    :param ScreenDriver: The screen driver to use. This driver can be recycled for future reuse
    :param top: Frame top most pixel in refrence frame of the screen (origin at top left corner)
    :param left: Frame left most pixel in reference frame of the screen (origin at top left corner)
    :param width: Frame width
    :param height: Frame height
    :return:
    """
    frame_size = {
        'top': top,
        'left': left,
        'width': width,
        'height': height
    }

    frame = ScreenDriver.grab(frame_size)

    return cv2.cvtColor(np.array(frame), cv2.COLOR_BGRA2BGR)


def liveframe(render: Callable[[np.ndarray, Any], np.ndarray], top: int = 0, left: int = 0, width: int = 1920,
              height: int = 1080, show: bool = True, **kwargs: Any) -> None:
    """ Draw debugging information into a live frame of a screen capture

    :param render: The function to render for each frame (passes the pixel array of the captured frame and other arguments included in
    kwards. Function should return pixel )
    :param top: Frame top most pixel in refrence frame of the screen (origin at top left corner)
    :param left: Frame left most pixel in reference frame of the screen (origin at top left corner)
    :param width: Frame width
    :param height: Frame height
    :param show: Bool to display or not using an external window
    :param kwargs: Additional arguments to pass to the render function
    :return: None
    """

    screen_driver = mss()

    while True:
        input_frame = grab_screen_frame(screen_driver, top, left, width, height)
        img = render(input_frame, **kwargs)

        if show:
            cv2.imshow("Live display", np.array(img))

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


if __name__ == "__main__":

    import time

    class TimeAverage:
        sum: float = 0.0
        num: int = 0
        zero: int = 0

        def average(self) -> float:
            return self.sum / self.num

        def __str__(self):
            return f"{self.average()},{self.num},{self.zero}"

    ScreenDriver = mss()
    time_average = TimeAverage()

    while time_average.num < 100:
        start = time.time()
        a = grab_screen_frame(ScreenDriver)
        time_average.sum += time.time() - start
        time_average.num += 1

    print(str(time_average))
