from difference import *
from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
from matplotlib import pyplot as plt
import numpy as np
import argparse
import imutils
import cv2

imc, cont_vis, im = getContourVisual('./VIS_301.png')
cv2.imshow('cont', imc)

cv2.waitKey(0)

