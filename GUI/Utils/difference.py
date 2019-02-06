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
	shifted = cv2.pyrMeanShiftFiltering(image, 15, 23)
	filt = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	filt = cv2.inRange(filt, (40, 0, 0), (80, 255, 255))

	thresh = cv2.threshold(filt, 67, 255, cv2.THRESH_BINARY_INV)[1]
	
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

	hulls = [cv2.convexHull(longest[0], False), cv2.convexHull(longest[1], False)]
	cv2.drawContours(image, [hulls[0]], -1, (0, 255, 0), 2)
	cv2.drawContours(image, [hulls[1]], -1, (0, 255, 0), 2)	

	#ensures that the 'left' foot will be transpose
	if hulls[0][0][0][0] > hulls[1][0][0][0]:
		np.roll(hulls, 1)
	''' La función retorna al final la imagen contornada, los puntos de los contornos y la imagen limpia'''
	return [image, hulls, image_clean]

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

def rectangularContour(points):
	p1 = np.min(points, axis=0)
	p2 = np.max(points, axis=0)

	return [p1, p2, np.array([[p1[0][0], p2[0][1]]]), np.array([[p1[0][1], p2[0][0]]])]

''' img1 = visual '''
def overlay(img1, img2, alpha = 0.5):
	vis_copy = img1.copy()
	cv2.addWeighted(img2, alpha, vis_copy, 1 - alpha, 0, vis_copy)

	return vis_copy

''' For now, just get a histogram of both feet '''
def maskFoot(t_img, points, sq=False):
	rows, cols = t_img.shape[:2]
	mask = np.zeros((rows, cols))

	if sq == True:
		cv2.rectangle(mask, points[0], points[1], 255, -1)
	else:	
		cv2.fillConvexPoly(mask, points, 1)
	
	mask = mask.astype(np.bool)
	out = np.zeros_like(t_img)
	out[mask] = t_img[mask]

	return out

''' We need the centroid of each masked foot to perform a geometric transformation '''
def getCentroid(point_list):
	x_list = [point[0][0] for point in point_list]
	y_list = [point[0][1] for point in point_list]
	leng = len(point_list)

	cx = sum(x_list) / leng
	cy = sum(y_list) / leng

	return (int(cx), int(cy))

def getRectangleCentroid(pi, pj):
	return (int(pi[0] + (pj[0] - pi[0]) / 2), int(pi[1] + (pj[1] - pi[1]) / 2))

def getDimensions(pi, pj):
	return (abs(pi[0] - pj[0]), abs(pi[1] - pj[1]))

''' resizes to fit the left foot to the right foot (experimental) '''
def cropAndResize(img, rect1, rect2):
	x, y = rect1[0][0][0], rect1[0][0][1]
	dims = getDimensions(rect1[0][0], rect1[1][0])
	rows, cols = img.shape[:2]
	print('(%s, %s)' % (x, y))
	print(dims)

	voidimg = np.zeros((rows, cols)).astype(np.uint8)
	crop = img[y:y+dims[1], x:x+dims[0]]
	ndim = getDimensions(rect2[0][0], rect2[1][0])

	crop = cv2.resize(crop, ndim)
	voidimg[0:ndim[1], 0:ndim[0]] = crop

	return [voidimg, ndim]

def drawStuff(img, rect, contour):
	#look for the highest point
	p1 = min(contour, key=lambda t: t[0][1])
	print(rect[2][0])
	#look for the lower outer point
	p2_f = min(contour, key=lambda t: t[0][0])
	p2 = p2_f
	for point in contour:
		if point[0][0] > p1[0][0] or point[0][1] > rect[2][0][1] * 0.8:
			continue
		if point[0][0] > p2[0][0] and point[0][1] > p2[0][1]:
			p2 = point
	
	#draw the contours and rects
	cv2.rectangle(img, tuple(rect[0][0]), tuple(rect[1][0]), 255, 1)
	#line from top (big toe) to bottom 
	l1 = [(p1[0][0], rect[0][0][1]), (p1[0][0], rect[1][0][1])]
	#horizontal line (fixed offset)
	l2 = [(rect[0][0][0], p2[0][1] + int(70)),  (rect[1][0][0], p2[0][1] + int(70))]
	#upper horizontal line
	l3 = [(p2_f[0][0], p2_f[0][1] - int(20)), (p1[0][0], p2_f[0][1] - int (20))]
	print(l3)
	cv2.line(img, l1[0], l1[1], 255)		
	#cut the lowest part on the half
	#done! 
	cv2.line(img, l2[0], l2[1], 255)
	cv2.line(img, l3[0], l3[1], 255)
	return img

def completeProcessing(imgdir_vis, imgdir_ir):
	COLOR = (0,0,255)

	cont_vis, im_vis = getContourVisual(imgdir_vis)[1:3]
	im_ir = getContourIR(imgdir_ir)[2]
	imtw = warpThermal(im_ir)

	rows, cols = im_vis.shape[:2]
	centroids = [ getCentroid(cont_vis[0]), getCentroid(cont_vis[1])]

	isolated = [ maskFoot(imtw, cont_vis[0]), maskFoot(imtw, cont_vis[1]) ]

	right_flipped = cv2.flip(isolated[0], 1)
	centroid0_flipped = (cols-centroids[0][0]-1, centroids[0][1])

	translation = tuple(np.subtract(centroids[1], centroid0_flipped))
	M = np.float32([[1, 0, translation[0]], [0, 1, translation[1]]])
	right_flipped = cv2.warpAffine(right_flipped, M, (cols, rows))

	diff = np.absolute(np.subtract(right_flipped.astype(np.float32), 
							isolated[1].astype(np.float32)))
	diff = diff.astype(np.uint8)
	#cv2.imshow('diffs', diff)

	for c in centroids:
		#print(c)
		cv2.circle(im_vis, c, 5, 0, -1)

	for h in cont_vis:
		cv2.drawContours(im_vis, [h], -1, 127, 2)

	return [diff, im_vis]

if __name__ == '__main__':
	# TO DO
	# Open the images outside the functions (and do the operations there)
	# Try to stretch the left foot to accomodate the borders
	# Get differences and normalize 
	# COO' STUFF
	i1, i2 = completeProcessing('./VIS_301.png', './IR_301.png')
	
	cv2.imshow('lol2', i1)
	cv2.imshow('lol', i2)

	cv2.waitKey(0)
