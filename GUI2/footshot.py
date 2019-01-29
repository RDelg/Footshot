import PySimpleGUI27 as sg 
import numpy as np 
import threading
import sys
import os
import cv2

from cv_cam import CvCamera
from ir_cam import ThermalCamera
import uvclite

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
		self.window = sg.Window('Testing window').Layout(self._layout).Finalize()
		#self.login = sg.Window('Footshot').Layout(self._form_layout)
		self.visual_cam = camera
		self.thread = threading.Thread(name="test", target=self.run)
		self.running = True
		self.visual_cam.start_streaming()
		self.thread.start()

	def update(self, image):
		#self.image = image
		norm = self.visual_cam.normalize(image)
		self.image = cv2.imencode('.png', norm)[1].tobytes()
		self.window.FindElement('thermal').Update(data=self.image)

	def run(self):
		while self.running:
			try:
				image = self.visual_cam.get_img_Y16(3)
				self.update(image)
			except Exception as e:
				print(e)	

	def read(self, timeout = 0):
		return self.window.Read(timeout)

	def close(self):
		self.running = False
		self.thread.join()
		cv2.destroyAllWindows()
		self.visual_cam.stop_streaming()
		self.window.Close()

	#login window methods
	def log_credentials(self, timeout = 0):
		return self.login.Read(timeout)

	def login_close(self):
		self.login.Close()

def footshot():
	with uvclite.UVCContext() as context:
		cam = ThermalCamera(context, 0x1e4e, 0x0100)
		win = GUI(cam)
		failed = False
		'''
		while True:
			event, values = win.log_credentials()
			if event is None or event == 'Salir':
				failed = True
				return
			elif event == 'Entrar':	
				print(values)
				win.login_close()
				break
		'''
		while not failed:
			event, values = win.read()
			if event is None or event == 'Exit':
				break

		win.close()

if __name__ == '__main__':
	footshot()