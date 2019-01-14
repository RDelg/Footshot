import cv2
import numpy
from matplotlib import pyplot as plt

img = cv2.imread('IR_1.png', 0)
plt.hist(img.ravel(), 256, [0, 256])
plt.show()