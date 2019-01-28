from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
from matplotlib import pyplot as plt
import numpy as np
import argparse
import imutils
import cv2

image = cv2.imread('./IR_21.png', -1)
cv2.normalize(image, image, 0, 65535, cv2.NORM_MINMAX)

np.right_shift(image, 8, image)

plt.hist(image.ravel(), 255 ,[0, 255])
plt.show()

image = np.uint8(image)

matrix = np.array([[ 1.19538782e+00, -1.00162838e-03, -9.37791263e+00],
 						[ 1.00162838e-03,  1.19538782e+00, -5.07336899e+01]])

rows, cols = image.shape[:2]
warped = cv2.warpAffine(image, matrix, (cols, rows))

cv2.imshow('wat', warped)
cv2.waitKey(0)