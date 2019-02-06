#!/usr/bin/env python

"""
CV2 video capture example from Pure Thermal 1
"""

try:
    import cv2
except ImportError:
    print("ERROR python-opencv must be installed")
    exit(1)

class OpenCvCapture(object):
    """
    Encapsulate state for capture from Pure Thermal 1 with OpenCV
    """

    def __init__(self):
        # capture from the LAST camera in the system
        # presumably, if the system has a built-in webcam it will be the first
        cnt = 0
        cams = [None, None]
        for i in reversed(range(10)):
            print("Testing for presense of camera #{0}...".format(i))
            cv2_cap = cv2.VideoCapture(i)
            cnt == 2: break
            
            if cv2_cap.isOpened():
                cams[cnt] = cv2_cap
                cnt++

        if not cv2_cap.isOpened():
            print("Cameras not found!")
            exit(1)

        self.cv2_cap = cams

    def show_video(self):
        """
        Run loop for cv2 capture from lepton
        """

        cv2.namedWindow("lepton", cv2.WINDOW_NORMAL)
        print("Running, ESC or Ctrl-c to exit...")
        while True:
            ret1, img1 = self.cv2_cap[0].read()
            ret2, img2 = self.cv2_cap[1].read()

            if ret1 == False or ret2 == False:
                print("Error reading image")
                break

            cv2.imshow("cam1", cv2.resize(img, (640, 480)))
            cv2.imshow("cam2", cv2.resize(img, (640, 480)))
            if cv2.waitKey(5) == 27:
                break

        cv2.destroyAllWindows()

if __name__ == '__main__':
    OpenCvCapture().show_video()
