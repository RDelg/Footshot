import cv2

class CoordinateStore:
    """Clase de eventos de doble click sobre alguna ventana opencv"""

    def __init__(self):
        self.points_ir = []
        self.points_vis = []
        self.points_transf = []

    def select_point_ir(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print x, y
            self.points_ir.append([x, y])
            return self.points_ir

    def select_point_vis(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print x, y
            self.points_vis.append([x, y])
            return self.points_vis

    def select_point_trans(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print x, y
            self.points_transf.append([x, y])
            return self.points_transf