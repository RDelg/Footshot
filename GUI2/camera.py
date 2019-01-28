import cv2 
import numpy as np

WIDTH = 3
HEIGHT = 4

cap = cv2.VideoCapture(0)
cap.set(WIDTH, 320)
cap.set(HEIGHT, 240)

frame = 0
while(True):
	ret, frame = cap.read()
	frame = cv2.flip(frame, 1)

	cv2.imshow('frame', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

	frame += 1
	
cap.release()
cv2.destroyAllWindows()


				