from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
from matplotlib import pyplot as plt
import numpy as np
import argparse
import imutils
import cv2

''' Obtiene los contornos de una imagen a color '''
def getContourVisual(img_dir):
	image_clean = cv2.imread(img_dir)
	image = image_clean.copy()
	''' Promedia los colores de los pixeles '''
	shifted = cv2.pyrMeanShiftFiltering(image, 16, 25)
	rows, cols = shifted.shape[:2]
	(B, G, R) = cv2.split(shifted)

	''' El fondo se vuelve negro '''
	for i in range(rows):
		for j in range(cols):
			if R[i][j] < 60:
				G[i][j] = 0; R[i][j] = 0; B[i][j] = 0;


	filt_shifted = cv2.merge([B, G, R]) #quizás valga la pena probar con los canales separados
	img = cv2.cvtColor(filt_shifted, cv2.COLOR_BGR2GRAY)

	thresh = cv2.threshold(img, 67, 255, cv2.THRESH_BINARY)[1]
	
	''' Luego se trazan todos los contornos...'''
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
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

	cv2.drawContours(image, [longest[0]], -1, (0, 255, 0), 2)
	cv2.drawContours(image, [longest[1]], -1, (0, 255, 0), 2)	

	''' La función retorna al final la imagen contornada, los puntos de los contornos y la imagen limpia'''
	return [image, longest, image_clean]

''' Obtiene los contornos de una imagen térmica (16-bits) '''
def getContourIR(img_dir, mirror=False):
	image = cv2.imread(img_dir, -1)
	cv2.normalize(image, image, 0, 65535, cv2.NORM_MINMAX)

	if mirror == True:
		rows, cols = image.shape[:2]
		M = cv2.getRotationMatrix2D((cols/2,rows/2), 180, 1)
		image = cv2.warpAffine(image, M, (cols, rows))

	np.right_shift(image, 8, image)
	image = np.uint8(image)
	image_clean = image.copy()

	thresh = cv2.threshold(image, 35, 255, cv2.THRESH_BINARY)[1]

	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)


	image = cv2.cvtColor(np.uint8(image), cv2.COLOR_GRAY2RGB)
	longest = [[], []]
	
	for cont in cnts:
		if len(cont) > len(longest[0]):
			longest[1] = longest[0]
			longest[0] = cont
		elif len(cont) > len(longest[1]):
			longest[1] = cont	

	cv2.drawContours(image, [longest[0]], -1, (0, 255, 0), 2)
	cv2.drawContours(image, [longest[1]], -1, (0, 255, 0), 2)	

	''' La función retorna al final la imagen (8-bits) contornada, los puntos de los contornos y la 
	imagen limpia '''
	return [image, longest, image_clean]

def warpThermal(img):
	#proudly hardcoded
	matrix = np.array([[ 1.19538782e+00, -1.00162838e-03, -9.37791263e+00],
 						[ 1.00162838e-03,  1.19538782e+00, -5.07336899e+01]])

	rows, cols = img.shape[:2]
	warped = cv2.warpAffine(img, matrix, (cols, rows))

	return warped			

''' img1 = visual '''
def overlay(img1, img2, alpha = 0.5):
	vis_copy = img1.copy()
	cv2.addWeighted(img2, alpha, vis_copy, 1 - alpha, 0, vis_copy)

	return vis_copy

''' For now, just get a histogram of both feet '''
def maskFoot(t_img, points):
	rows, cols = t_img.shape[:2]
	mask = np.zeros((rows, cols))

	cv2.fillConvexPoly(mask, points, 1)
	mask = mask.astype(np.bool)

	out = np.zeros_like(t_img)
	out[mask] = t_img[mask]

	return out


if __name__ == '__main__':
	cont_ir, im1 = getContourIR('./IR_1.png')[1:3]
	cont_vis, im2 = getContourVisual('./VIS_1.png')[1:3]
	im1w = warpThermal(im1)

	foot1 = maskFoot(im1, cont_ir[0])
	plt.hist(foot1.ravel(), 255, [1, 255], histtype='step')

	foot2 = maskFoot(im1, cont_ir[1])
	plt.hist(foot2.ravel(), 255, [1, 255], histtype='step')
	plt.show()
	#img_color = cv2.applyColorMap(im1w, cv2.COLORMAP_JET)
	#ov = overlay(im2, img_color)

	cv2.imshow('foot1', foot1)
	cv2.imshow('foot2', foot2)
	cv2.waitKey(0)
