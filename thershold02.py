import cv2
import numpy as np


class thershold:
    def __init__(self):
        self.kernelOpen = np.ones((5, 5))
        self.kernelClose = np.ones((20, 20))
        self.rois = np.array((480, 640))
    #def capture(self):

    def readImage(self, i, carpeta):
        # Read
        path_vis = "./%s/VIS_%d.png" % (carpeta, i)
        path_ir = "./%s/IR_%d.png" % (carpeta, i)
        vis = cv2.imread(path_vis)
        ir = cv2.imread(path_ir)
        return vis, ir

    def raw_to_8bit(self, data):
        cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(data, 8, data)
        return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

    def green(self, img):
        # convert to hsv
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # mask of green (36,0,0) ~ (70, 255,255)
        mask1 = cv2.inRange(hsv, (58, 129, 116), (78, 149, 196))
        # mask of espuma
        mask2 = cv2.inRange(hsv, (52, 143, 85), (72, 163, 165))

        #mask3 = cv2.inRange(hsv, (95, 63, 159), (115, 83, 239))
        # final mask and masked
        mask = cv2.bitwise_or(mask1, mask2)
        target = cv2.bitwise_and(img, img, mask=mask).astype(np.uint8)
        kernel = np.ones((5, 3), np.uint8)

        img_erosion = cv2.dilate(target, kernel, iterations=4)
        return img_erosion

    def open_close(self, img):
        maskOpen = cv2.morphologyEx(img, cv2.MORPH_OPEN, self.kernelOpen)
        maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, self.kernelClose)
        return maskClose

    def convertGray(self, img):
        # Se convierte a grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return gray

    def addBorder(self, img):
        # Resize image vis for the best find contour
        bordersize = 10
        border_img = cv2.copyMakeBorder(img, right=bordersize, left=bordersize, top=bordersize, bottom=bordersize,
                                        borderType=cv2.BORDER_CONSTANT, value=[255, 255, 255])

        return border_img

    def findContour(self, img):
        contour, hier = cv2.findContours(img.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        return contour

    def convertRGB(self, img):
        # From grayscale to rgb for contourn color

        color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        return color_img

    def drawContour(self, img, contour):
        # And fill them
        gray_img = img.copy()
        crops = []

        for c in contour:
            area_obj = cv2.contourArea(c)

            # Filter
            if 10000 < area_obj < 90000:
                rect = cv2.minAreaRect(c)
                crop = self.crop_foot(gray_img, rect)
                crops.append(crop)
                box = cv2.boxPoints(rect)
                box = np.int0(box)

                rois = np.append(self.rois, [box[0], box[2]])
                cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
                cX, cY = self.findCenter(img, c, True)
                cv2.line(img, (cX, cY), (100, 100), (0, 255, 0))
        # print crops
        return img, gray_img, crops

    def findCenter(self, image, contour, draw):
        M = cv2.moments(contour)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        if draw:
            cv2.putText(image, "center", (cX - 20, cY - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        return cX, cY

    def compare(self, leftfoot, rightfoot):
        dim = (rightfoot.shape[1], rightfoot.shape[0])
        leftfoot = cv2.flip(cv2.resize(leftfoot, dim), 1)
        diference = cv2.subtract(rightfoot, leftfoot)
        #diference = abs(rightfoot - leftfoot)
        #diference = self.raw_to_8bit(diference)

        return diference

    def crop_foot(self, img, rect):

        mult = 1.2
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        #cv2.drawContours(img, [box], 0, (0, 255, 0), 2)  # this was mostly for debugging you may omit

        W = rect[1][0]
        H = rect[1][1]

        Xs = [i[0] for i in box]
        Ys = [i[1] for i in box]
        x1 = min(Xs)
        x2 = max(Xs)
        y1 = min(Ys)
        y2 = max(Ys)

        rotated = False
        angle = rect[2]

        if angle < -45:
            angle += 90
            rotated = True

        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
        size = (int(mult * (x2 - x1)), int(mult * (y2 - y1)))
        #cv2.circle(img, center, 10, (0, 255, 0), -1)  # again this was mostly for debugging purposes

        M = cv2.getRotationMatrix2D((size[0] / 2, size[1] / 2), angle, 1.0)

        cropped = cv2.getRectSubPix(img, size, center)
        cropped = cv2.warpAffine(cropped, M, size)

        croppedW = W if not rotated else H
        croppedH = H if not rotated else W

        croppedRotated = cv2.getRectSubPix(cropped, (int(croppedW * mult), int(croppedH * mult)),
                                           (size[0] / 2, size[1] / 2))

        return croppedRotated


if __name__ == "__main__":
    thershold = thershold()
    for i in range(1, 220):
        vis, ir = thershold.readImage(i, 'Marcela')
        vis_green = thershold.green(vis)
        green_close = thershold.open_close(vis_green)
        green_gray = thershold.convertGray(green_close)
        green_gray_border = thershold.addBorder(green_gray)
        contour = thershold.findContour(green_gray_border)
        green_color = thershold.convertRGB(green_gray_border)
        result = thershold.drawContour(green_color, contour)

        cv2.imshow('Detection', result)
        cv2.waitKey(10)
