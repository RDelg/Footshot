import numpy as np 
import cv2

class CvCamera(object):
	def __init__(self, cam_id, fps=30, resolution=(320, 240)):
		self.cap = cv2.VideoCapture(cam_id)
		assert self.cap.isOpened(), "Camera not found..."
		self.resolution = resolution
		self.fps = fps
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
		self.cap.set(cv2.CAP_PROP_FPS, fps)
		self.frame = 0

	def get_frame(self):
		ret, frame = self.cap.read()
		if not ret:
			return None
		#flips?
		self.frame += 1
		return frame

	def stop(self):
		self.cap.release()


if __name__ == '__main__':
	cam = CvCamera(0)

	cv2.namedWindow('wat', cv2.WINDOW_NORMAL)
	while True:
		img = cam.get_frame()
		if img is None:
			break

		cv2.imshow('wat', img)
		order = cv2.waitKey(1) & 0xFF 

		if order == ord('q'):
			break

		elif order == ord('s'):
			cv2.imwrite('wew.png', img)

	cam.stop()
	cv2.destroyAllWindows()	