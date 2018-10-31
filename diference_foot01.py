#!/usr/bin/env python
# -*- coding: utf-8 -*-
import usb

from uvctypes import *

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

import numpy as np
from numpy import array
import cv2

# Importacion de Clases
from thershold01 import thershold
from coordinateStore01 import CoordinateStore

# Instacia de la clase thershold
thershold = thershold()

# Instancia de la clase CoordinateStore()#
coordinateStore1 = CoordinateStore()
cv2.namedWindow('Grayscale')
cv2.namedWindow('Visible')
# Se indica en que ventanas se esperaran los eventos##
cv2.setMouseCallback('Grayscale', coordinateStore1.select_point_ir)
cv2.setMouseCallback('Visible', coordinateStore1.select_point_vis)

carpeta = raw_input('Ingrese nombre de la carpeta:')
print type(carpeta)
while True:

    # Se leen las imagenes a procesar
    img = cv2.imread('./%s/IR_1.png' % carpeta, -1)
    img_visual = cv2.imread('./%s/VIS_1.png' % carpeta, 0)

    leer = raw_input('Leer datos de calibracion si/no:')
    if leer == "si":
        data = np.loadtxt("./calibration/calibration2.txt")
        points_vis = data[0:5]
        points_ir = data[5:10]
        print points_vis, points_ir
        break
    elif leer == "no":

        while True:

            """While de refresco de imagens para actualizacion de overlays"""

            cv2.imshow('Grayscale', img)
            cv2.imshow('Visible', img_visual)
            cv2.waitKey(1)

            for x1, y1 in coordinateStore1.points_ir:
                cv2.circle(img, (x1, y1), 10, (255, 0, 255))

            for x2, y2 in coordinateStore1.points_vis:
                cv2.circle(img_visual, (x2, y2), 10, (255, 0, 255))
            if len(coordinateStore1.points_ir) & len(coordinateStore1.points_vis) == 5:
                points_vis = coordinateStore1.points_vis
                points_ir = coordinateStore1.points_ir
                cv2.destroyAllWindows()
                break

        write_cal = raw_input("Desea guadar datos de calibracion? si/no:")
        if write_cal == "si":
            points_cal = [np.array(coordinateStore1.points_vis), np.array(coordinateStore1.points_ir)]
            points_cal = np.concatenate(points_cal)
            # Save data calibration
            np.savetxt("./calibration/calibration2.txt", points_cal)
            break
        elif write_cal == "no":
            break
        else:
            print "El valor ingresado no es valido"

# Se preparan los puntos de features en 3D y float32 (Como lo pide estimateRigidform)""
points1 = array([points_ir]).astype(np.float32)
points2 = array([points_vis]).astype(np.float32)


# Se calcula la matriz de Transformacion
transformation = cv2.estimateRigidTransform(points1, points2, False)
print transformation
rows, cols = img.shape[:2]

# Se obtiene imagen regenerada
ir_transf = cv2.warpAffine(img_visual, transformation, (cols, rows))


#cv2.namedWindow('Warp_Visual')
cv2.setMouseCallback('Warp_Visual', coordinateStore1.select_point_trans)




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
    )

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

        libuvc.uvc_get_stream_ctrl_format_size(devh, byref(ctrl), UVC_FRAME_FORMAT_Y16,
                                               frame_formats[0].wWidth, frame_formats[0].wHeight,
                                               int(1e7 / frame_formats[0].dwDefaultFrameInterval)
                                               )

        res = libuvc.uvc_start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
        if res < 0:
            print("uvc_start_streaming failed: {0}".format(res))
            exit(1)

        try:
            cam = cv2.VideoCapture(0)
            i = 0
            while True:

                data = q.get(True, 500)
                data = cv2.flip(data, -1)
                if data is None:
                    break
                ir = cv2.resize(data[:, :], (640, 480))

                ret_val, img_visual = cam.read()
                i = i + 1
                ir_transf = cv2.warpAffine(ir, transformation, (cols, rows))
                ir_color = thershold.convertRGB(ir_transf)
                ir_transf = thershold.raw_to_8bit(ir_transf)
                vis_green = thershold.green(img_visual)
                green_close = thershold.open_close(vis_green)
                green_gray = thershold.convertGray(green_close)
                contour = thershold.findContour(green_gray)
                green_color = thershold.convertRGB(green_gray)
                result_vis, result_vis_gray, crops_vis = thershold.drawContour(img_visual, contour)

                result_ir, result_ir_gray, crops_ir = thershold.drawContour(ir_transf, contour)
                try:
                    diference = thershold.compare(crops_ir[0], crops_ir[1])
                    cv2.imshow('Diference', diference)
                    #cv2.moveWindow('Diference', 3200, 1500)
                    cv2.imshow('Vis left', crops_vis[0])
                    #cv2.moveWindow('Vis left', 2000, 0)
                    cv2.imshow('Vis right', crops_vis[1])
                    #cv2.moveWindow('Vis right', 4200, 0)
                    cv2.imshow('Ir left', crops_ir[0])
                    #cv2.moveWindow('Ir left', 2400, 0)
                    cv2.imshow('Ir right', crops_ir[1])
                    #cv2.moveWindow('Ir right', 3800, 0)
                    # cv2.imshow('Color', vis_green)
                    cv2.imshow('Color', result_vis)
                    #cv2.moveWindow('Color', 3000, 0)
                    cv2.imshow('Detection', result_ir)
                    #cv2.moveWindow('Detection', 3000, 600)
                    cv2.waitKey(200)
                except:
                    pass

                if cv2.waitKey(1) & 0xFF == ord('s'):
                    i = i + 1
                    cv2.imwrite('./Juan Pablo/VIS_%d.png' % i, img_visual)
                    cv2.imwrite('./Juan Pablo/IR_%d.png' % i, img)

                    print 'Save Images'

            cv2.destroyAllWindows()
        finally:
            libuvc.uvc_stop_streaming(devh)

        print("done")
    finally:
        libuvc.uvc_unref_device(dev)
finally:
    libuvc.uvc_exit(ctx)


