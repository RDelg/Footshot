import PySimpleGUI27 as sg 
import numpy as np 
import threading
import sys
import os
import cv2

from cv_cam import CvCamera

class GUI(object):

	_left_frame = [
					[sg.Image(data='', background_color='gray', size=(320, 240),
						key='thermal', tooltip='Imagen IR')]
				  ]
	#define all windows and sectors
	_layout = [ 
				[
					sg.Frame('Infrarrojo', _left_frame,
								font='Any 12', title_color='blue'),
					sg.Frame('Visual', [],
								font='Any 12', title_color='blue')
				],
				[sg.Text('Window')],
				[sg.Input(do_not_clear=True)],
				[sg.Button('Read'), sg.Exit()]
			  ]

	_form_layout = [
					[sg.Text('Ingresar')],
					[sg.Text('RUT'), sg.InputText()],
					[sg.Text('PIN'), sg.InputText(password_char='*')],
					[sg.Button('Entrar', size=(4, 1), font="Helvetica 14"), sg.Button('Salir', font="Helvetica 14")]
	]

	def __init__(self, camera):
		self.window = sg.Window('Testing window').Layout(self._layout)
		self.login = sg.Window('Footshot').Layout(self._form_layout)
		self.visual_cam = camera
		self.thread = threading.Thread(name="test", target=self.run)
		self.running = True
		self.thread.start()

	def update(self, image):
		#self.image = image
		self.image = cv2.imencode('.png', image)[1].tobytes()
		self.window.FindElement('thermal').Update(data=self.image)

	def run(self):
		while self.running:
			try:
				image = self.visual_cam.get_frame()
				print(image)
				self.update(image)
			except Exception as e:
				print(e)	

	def read(self, timeout = 0):
		return self.window.Read(timeout)

	def close(self):
		self.running = False
		self.thread.join()

		self.visual_cam.stop()
		self.window.Close()

	#login window methods
	def log_credentials(self, timeout = 0):
		return self.login.Read(timeout)

	def login_close(self):
		self.login.Close()

def footshot():
	cam = CvCamera(0)
	win = GUI(cam)
	failed = False

	while True:
		event, values = win.log_credentials()
		if event is None or event == 'Salir':
			failed = True
			return
		elif event == 'Entrar':	
			print(values)
			win.login_close()
			break

	while not failed:
		event, values = win.read()
		if event is None or event == 'Exit':
			break
		print(values)

	win.close()

if __name__ == '__main__':
	footshot()