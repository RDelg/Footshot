from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
from matplotlib import pyplot as plt
import numpy as np
import argparse
import imutils
import cv2

'''Este fichero obtiene los contornos de los pies en las fotos sacadas por el Footshot'''

image = cv2.imread('./VIS_1.png')
''' Promedia los colores de los pixeles '''
shifted = cv2.pyrMeanShiftFiltering(image, 16, 25)

cv2.imshow('shifted', shifted)
  
rows, cols = shifted.shape[:2]
(B, G, R) = cv2.split(shifted)

''' El fondo se vuelve negro '''
for i in range(rows):
	for j in range(cols):
		if R[i][j] < 60:
			G[i][j] = 0; R[i][j] = 0; B[i][j] = 0;

filt_shifted = cv2.merge([B, G, R])
img = cv2.cvtColor(filt_shifted, cv2.COLOR_BGR2GRAY)

thresh = cv2.threshold(img, 67, 255, cv2.THRESH_BINARY)[1]
plt.hist(img.ravel(), 256, [0, 256])
plt.show()

cv2.imshow("filtered", thresh)
''' Luego se trazan todos los contornos...'''

cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
print("[INFO] {} unique contours found".format(len(cnts)))

longest = [[], []]

''' ...y nos quedamos con el/los contornos mas largos '''
for cont in cnts:
	if len(cont) > len(longest[0]):
		longest[1] = longest[0]
		longest[0] = cont
	elif len(cont) > len(longest[1]):
		longest[1] = cont	

cv2.drawContours(image, [longest[0]], -1, (0, 255, 0), 2)
cv2.drawContours(image, [longest[1]], -1, (0, 255, 0), 2)		
# show the output image

cv2.imshow("Image", image)
cv2.waitKey(0)