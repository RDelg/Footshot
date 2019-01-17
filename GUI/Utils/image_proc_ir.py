from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
from matplotlib import pyplot as plt
import numpy as np
import argparse
import imutils
import cv2

image = cv2.imread('./IR_1.png', -1)
cv2.normalize(image, image, 0, 65535, cv2.NORM_MINMAX)

np.right_shift(image, 8, image)

plt.hist(image.ravel(), 255 ,[0, 255])
plt.show()

image = np.uint8(image)

thresh = cv2.threshold(image, 35, 255, cv2.THRESH_BINARY)[1]

cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
print("[INFO] {} unique contours found".format(len(cnts)))


image = cv2.cvtColor(np.uint8(image), cv2.COLOR_GRAY2RGB)

for (i, c) in enumerate(cnts):
	# draw the contour
	((x, y), _) = cv2.minEnclosingCircle(c)
	#cv2.putText(image, "#{}".format(i + 1), (int(x) - 10, int(y)),
	#	cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
	cv2.drawContours(image, [c], -1, (0, 255, 0), 2)

cv2.imshow('wat', image)
cv2.imshow('wat2', thresh)
cv2.waitKey(0)