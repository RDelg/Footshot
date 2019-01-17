import cv2
import numpy
from matplotlib import pyplot as plt

img = cv2.imread('IR_1.png', -1)
img2 = cv2.imread('VIS_1.png', 0)

cv2.normalize(img, img, 0, 65535, cv2.NORM_MINMAX)
rows, cols = img.shape[:2]
M = cv2.getRotationMatrix2D((cols/2,rows/2), 180, 1)
img_rotated = cv2.warpAffine(img, M, (cols, rows))
#done

cv2.imshow('img', img_rotated)
cv2.imshow('img2', img2)
plt.hist(img.ravel(), 256, [0, 256])
plt.show()