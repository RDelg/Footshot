#!/usr/bin/env python
# -*- coding: utf-8 -*-
import usb

from uvctypes import *
import time
import cv2
import numpy as np

try:
    from queue import Queue
except ImportError:
    from Queue import Queue
import platform

busses = usb.busses()
for bus in busses:
    devices = bus.devices
    for dev in devices:
        print repr(dev)
        print "  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct)
        print "Manufacturer:", dev.iManufacturer
        print "Serial:", dev.iSerialNumber
        print "Product:", dev.iProduct

BUF_SIZE = 2
q = Queue(BUF_SIZE)


class CoordinateStore:
    def __init__(self):
        self.points_ir = []
        self.points_vis = []

    def select_point_ir(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print x, y
            self.points_ir.append((x, y))
            return self.points_ir

    def select_point_vis(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print x, y
            self.points_vis.append((x, y))
            return self.points_vis


# instantiate class
coordinateStore1 = CoordinateStore()


def py_frame_callback(frame, userptr):
    array_pointer = cast(frame.contents.data, POINTER(c_uint16 * (frame.contents.width * frame.contents.height)))
    data = np.frombuffer(
        array_pointer.contents, dtype=np.dtype(np.uint16)
    ).reshape(
        frame.contents.height, frame.contents.width
    )  # no copy

    # data = np.fromiter(
    #   frame.contents.data, dtype=np.dtype(np.uint8), count=frame.contents.data_bytes
    # ).reshape(
    #   frame.contents.height, frame.contents.width, 2
    # ) # copy

    if frame.contents.data_bytes != (2 * frame.contents.width * frame.contents.height):
        return

    if not q.full():
        q.put(data)


PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(py_frame_callback)


def ktof(val):
    return 1.8 * ktoc(val) + 32.0


def ktoc(val):
    return (val - 27315) / 100.0


def raw_to_8bit(data):
    cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(data, 8, data)
    return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)


cv2.namedWindow('Grayscale')
cv2.namedWindow('Visible')
cv2.setMouseCallback('Grayscale', coordinateStore1.select_point_ir)
cv2.setMouseCallback('Visible', coordinateStore1.select_point_vis)

ctx = POINTER(uvc_context)()
dev = POINTER(uvc_device)()
devh = POINTER(uvc_device_handle)()
ctrl = uvc_stream_ctrl()

res = libuvc.uvc_init(byref(ctx), 0)
if res < 0:
    print("uvc_init error")
    exit(1)

try:
    res = libuvc.uvc_find_device(ctx, byref(dev), 0x1e4e, 0x0100, 0)
    #res = libuvc.uvc_find_device(ctx, byref(dev), 0x0001, 0x082b, 0)

    if res < 0:
        print("uvc_find_device error")
        exit(1)

    try:

        res = libuvc.uvc_open(dev, byref(devh))
        if res < 0:
            print("uvc_open error")
            exit(1)

        print("device opened!")

        print_device_info(devh)
        print_device_formats(devh)

        frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
        if len(frame_formats) == 0:
            print("device does not support Y16")
            exit(1)
        print frame_formats[0].wWidth
        print frame_formats[0].wHeight
        print 1e7 / frame_formats[0].dwDefaultFrameInterval
        libuvc.uvc_get_stream_ctrl_format_size(devh, byref(ctrl), UVC_FRAME_FORMAT_Y16,
                                               frame_formats[0].wWidth, frame_formats[0].wHeight,
                                               int(1e7 / frame_formats[0].dwDefaultFrameInterval)
                                               )

        res = libuvc.uvc_start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
        if res < 0:
            print("uvc_start_streaming failed: {0}".format(res))
            exit(1)

        try:
            cam = cv2.VideoCapture(1)
            i = 0
            while True:

                data = q.get(True, 500)
                if data is None:
                    break
                data = cv2.resize(data[:, :], (640, 480))
                data = cv2.flip(data, -1)
                ret_val, img_visual = cam.read()
                img = raw_to_8bit(data)
                #for x1, y1 in coordinateStore1.points_ir:
                    #cv2.circle(img, (x1, y1), 10, (255, 0, 255))
                cv2.imshow('Grayscale', img)
                cv2.imshow('Visible', img_visual)
                cv2.waitKey(1)



                #for x2, y2 in coordinateStore1.points_vis:
                    #cv2.circle(img_visual, (x2, y2), 10, (255, 0, 255))
                #print coordinateStore1.points_vis
                if cv2.waitKey(1) & 0xFF == ord('s'):
                    i = i + 1
                    cv2.imwrite('./paciente5/VIS_%d.png' % i, img_visual)
                    cv2.imwrite('./paciente5/IR_%d.png' % i, data)

                    #cv2.imwrite('VIS.png', img_visual)
                    #cv2.imwrite('IR.png', img)
                    print 'Save Images'

            cv2.destroyAllWindows()
        finally:
            libuvc.uvc_stop_streaming(devh)

        print("done")
    finally:
        libuvc.uvc_unref_device(dev)
finally:
    libuvc.uvc_exit(ctx)
