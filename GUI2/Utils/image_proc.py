from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider
from difference import maskFoot
import numpy as np
import argparse
import imutils
import cv2

'''Este fichero obtiene los contornos de los pies en las fotos sacadas por el Footshot'''

image_clean = cv2.imread('./VIS_1.png')
''' Promedia los colores de los pixeles '''
image = cv2.pyrMeanShiftFiltering(image_clean, 16, 25)
#image = cv2.GaussianBlur(image_clean, (3, 3), 0)
filt = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

cv2.imshow('ttt', filt)

filt = cv2.blur(filt, (5, 5))
filt = cv2.inRange(filt, (0, 30, 60), (125, 75, 200))

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
hsv_d = cv2.dilate(filt, kernel)
#filt = cv2.threshold(filt, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

cv2.imshow('filt1', hsv_d)	

cnts = cv2.findContours(hsv_d.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

longest = [[], []]

''' ...y nos quedamos con el/los contornos mas largos '''
for cont in cnts:
	if len(cont) > len(longest[0]):
		longest[1] = longest[0]
		longest[0] = cont
	elif len(cont) > len(longest[1]):
		longest[1] = cont	

hulls = [cv2.convexHull(longest[0], False), cv2.convexHull(longest[1], False)]
#cv2.drawContours(image_clean, [longest[0]], -1, (0, 255, 0), 2)
#cv2.drawContours(image_clean, [longest[1]], -1, (0, 255, 0), 2)

rows, cols = image_clean.shape[:2]
mask = np.zeros((rows, cols))

cv2.fillConvexPoly(mask, hulls[0], 255)
cv2.fillConvexPoly(mask, hulls[1], 255)
cv2.imshow('mask', mask.astype(np.uint8))


mask = mask.astype(np.bool)
out = np.zeros_like(image_clean)
out[mask] = image_clean[mask]	

cv2.imshow('dsda', image_clean)
cv2.imshow('ads', out)
cv2.waitKey(0)	