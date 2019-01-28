import logging
import cv2
import numpy as np

import uvclite

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: [%(levelname)s] (%(threadName)-10s) %(message)s'
                    )

class ThermalCamera(object):
    _Y16 = uvclite.libuvc.uvc_frame_format.UVC_FRAME_FORMAT_Y16

    def __init__(self, context, vendor_id=0, product_id=0, width=160, height=120, fps=9):
        self.context = context
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.fps = fps
        self.width = width
        self.height = height
        self.frame_format = _Y16
        self._find_device()
        self._open()
        self._set_stream_format()

        self.is_streaming = False

    def _open(self):
        self.device.open()

    def _find_devices(self):
        self.device = self.context.find_device(self.vendor_id, self.product_id)

    def _set_stream_format(self):
        self.device.set_stream_format(
            self.frame_format, self.width,
            self.height, self.fps
            )

    def start_streaming(self):
        if not self.is_streaming:
            self.device.start_streaming()
            self.is_streaming = True

    def stop_streaming(self):
        if self.is_streaming:
            self.device.stop_streaming()
            self.is_streaming = False

    def _get_frame(self, timeout):
        assert(self.is_streaming, "Not streaming")
        return self.device.get_frame(timeout)

    def normalize(self, img):
        normalized = None
        cv2.normalize(img, normalized, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(normalized, 8, normalized)
        normalized = cv2.cvtColor(np.uint(normalized), cv2.COLOR_GRAY2RGB)
        return normalized

    def get_img_Y16(self, timeout, size=(320, 240)):
        frame = self._get_frame(timeout)
        while frame.size != (2 * self.height * self.width):
            frame = self._get_frame(timeout)

        data = np.frombuffer(frame.data, dtype=np.uint16)
                        .reshape(self.height, self.width)
        if self.width != size[0] or self.height != size[1]:
            data = cv2.resize(data, size)

        return data

if __name__ == '__main__':
    with uvclite.UVCContext() as context:
        cam = ThermalCamera(context, 0x1e4e, 0x0100)
        cam.start_streaming()

        while True:
            img = cam.get_img_Y16(0)
            img = cam.normalize(img)

            cv2.imshow('img', img)

        cam.stop_streaming()
        cv2.destroyAllWindows()