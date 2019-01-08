import logging
import threading
import sys
import os
from time import sleep

import cv2
import numpy as np

import uvclite
import PySimpleGUI27 as sg


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: [%(levelname)s] (%(threadName)-10s) %(message)s'
                    )


class Camera(object):

  _Y16 = uvclite.libuvc.uvc_frame_format.UVC_FRAME_FORMAT_Y16

  def __init__(self, context, vendor_id=0, product_id=0, frame_format=_Y16, width=160, height=120, frame_rate=9):
    self.context = context
    self.vendor_id = vendor_id
    self.product_id = product_id
    self.frame_format = frame_format
    self.width = width
    self.height = height
    self.frame_rate = frame_rate
    self._find_device()
    self._open()
    self._set_stream_format()

    self.is_streaming = False

  def _open(self):
    logging.debug("Disp: (%s , %s) ABRIENDO." %
                  (self.vendor_id, self.product_id))
    self.device.open()
    logging.debug("Disp: (%s , %s) ABIERTO." %
                  (self.vendor_id, self.product_id))

  def _find_device(self):
    logging.debug("Disp: (%s , %s) BUSCANDO." %
                  (self.vendor_id, self.product_id))
    self.device = self.context.find_device(self.vendor_id, self.product_id)
    logging.debug("Disp: (%s , %s) ENCONTRADO." %
                  (self.vendor_id, self.product_id))

  def _set_stream_format(self):
    self.device.set_stream_format(
        self.frame_format, self.width, self.height, self.frame_rate)
    logging.debug("Disp: (%s , %s) CONFIGURADO a (%s, %s, %s, %s)." % (
        self.vendor_id, self.product_id, self.frame_format, self.width, self.height, self.frame_rate))

  def start_streaming(self):
    if not self.is_streaming:
      logging.debug("Disp: (%s , %s) EMPEZANDO STREAM." %
                    (self.vendor_id, self.product_id))
      self.device.start_streaming()
      logging.debug("Disp: (%s , %s) STREAM INICIADO." %
                    (self.vendor_id, self.product_id))
      self.is_streaming = True

  def stop_streaming(self):
    if self.is_streaming:
      logging.debug("Disp: (%s , %s) DETENIENDO STREAM." %
                    (self.vendor_id, self.product_id))
      self.device.stop_streaming()
      self.is_streaming = False
      logging.debug("Disp: (%s , %s) STREAM DETENIDO." %
                    (self.vendor_id, self.product_id))

  def _get_frame(self, timeout):
    assert self.is_streaming, "La camara no esta en modo streaming"
    return self.device.get_frame(timeout)

  def get_img_Y16(self, timeout, size=(320, 240)):
    frame = self._get_frame(timeout)
    # La camara no siempre devuelve un frame completo
    while frame.size != (2*self.height*self.width):
      frame = self._get_frame(timeout)
    # Convertimos a un array de numpy
    data = np.frombuffer(frame.data, dtype=np.uint16).reshape(
        self.height, self.width)
    # Verificando reescalado
    if self.width != size[0] or self.height != size[1]:
      data = cv2.resize(data, size)
    cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
    # 16bits a 8bits
    np.right_shift(data, 8, data)
    # to RGB
    img = cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)
    return img
    # Normalizado
    # return cv2.imencode('.png', img)[1].tobytes()

  def get_img_MJPEG(self, timeout, size=(320, 240)):
    frame = self._get_frame(timeout)
    data = np.frombuffer(frame.data, dtype=np.uint16)
    if self.width != size[0] or self.height != size[1]:
      data = cv2.resize(data, size)
    return cv2.imdecode(data, 1)
    # return cv2.imencode('.png', img)[1].tobytes()

  # TODO
  @staticmethod
  def imwrite(path, img):
    cv2.imwrite(path, img)

  # def __del__(self):
  #   if self.is_streaming:
  #     self.device.stop_streaming()
  #     self.is_streaming == False
  #   self.device.close()


class FootGui(object):

  _left_frame = [
      [sg.Image(data='', background_color='gray', size=(
          320, 240), key='infrarrojo', tooltip='Imagen IR')]
  ]
  _right_frame = [
      [sg.Image(data='', background_color='green', size=(
          320, 240), key='visual', tooltip='Imagen Visual')]
  ]
  _layout = [
      [
          sg.Frame('Infrarrojo', _left_frame,
                   font='Any 12', title_color='blue'),
          sg.Frame('Visible', _right_frame,
                   font='Any 12', title_color='blue')
      ],
      [
          sg.T(' ' * 10),
          sg.Button('Record', size=(5, 1), font='Helvetica 14'),
          sg.Button('Stop', size=(5, 1), font='Any 14'),
          sg.Button('Exit', size=(5, 1), font='Helvetica 14'),
          sg.Button('About', size=(5, 1), font='Any 14'), #maybe change name??
          sg.Button('New Folder', size=(5, 1), font='Helvetica 14')
      ],
      [
          sg.T(' ' * 10)
      ]
  ]

  _capture_layout = [[sg.Text('Tomando capturas')],
                     [sg.ProgressBar(10, orientation='h',
                                     size=(20, 20), key='progressbar')]]

  def __init__(self, left_dev, right_dev):
    self.window = sg.Window('Footshot', grab_anywhere=False,
                            icon='Isotipo.ico').Layout(self._layout)
    self.left_dev = left_dev
    self.right_dev = right_dev
    self.is_left_capturing = False
    self.is_right_capturing = False
    self.save_left = 0
    self.save_right = 0
    self.start_streaming()
    self.start_capturing()
    self.lock = threading.RLock()

  def start_streaming(self):
    if not self.left_dev.is_streaming and not self.left_dev.is_streaming:
      self.left_dev.start_streaming()
      self.right_dev.start_streaming()
      sleep(1)

  def stop_streaming(self):
    if self.left_dev.is_streaming and self.left_dev.is_streaming:
      self.left_dev.stop_streaming()
      self.right_dev.stop_streaming()

  # Consider setting a timeout to prevent close freezing
  def read(self, timeout=None):
    return self.window.Read(timeout)

  def update_left(self, img_left):
  	#local rotation of the left frame
	rows, cols= img_left.shape[:2]
	M = cv2.getRotationMatrix2D((cols/2,rows/2), 180, 1)
	img_left_rotated = cv2.warpAffine(img_left, M, (cols, rows))
  	#done

	self.img_left = cv2.imencode('.png', img_left_rotated)[1]
	self.window.FindElement('infrarrojo').Update(data=self.img_left.tobytes())

  def update_right(self, img_right):
  	self.img_right = cv2.imencode('.png', img_right)[1].tobytes()
	self.window.FindElement('visual').Update(data=self.img_right)

  def run_left(self):
    if not self.is_left_capturing:
      self.is_left_capturing = True
      while self.is_left_capturing and self.left_dev.is_streaming:
        try:
          img_left = self.left_dev.get_img_Y16(0)
          self.update_left(img_left)
          # Guardando imagen
          if self.save_left > 0:
            self.lock.acquire()
            logging.debug('Guardando imagen %s' % self.save_left)
            self.left_dev.imwrite('%sIR_%s.png' % (self.folder_name, self.save_left), img_left)
            self.save_left += -1

            # Update ventana de progreso
            self.window2.FindElement('progressbar').UpdateBar(-1 * (self.save_left - self.n_imgs))
            if self.save_left == 0:
              self.window2.Close()

            self.lock.release()
        except uvclite.UVCError as e:
          logging.debug(e)
        except Exception as e:
          logging.debug(e)

  def run_right(self):
    if not self.is_right_capturing:
      self.is_right_capturing = True
      while self.is_right_capturing and self.right_dev.is_streaming:
        try:
          img_right = self.right_dev.get_img_MJPEG(0)
          self.update_right(img_right)
          if self.save_right > 0:
            self.lock.acquire()
            logging.debug('Guardando imagen %s' % self.save_right)
            self.right_dev.imwrite('%sVIS_%s.png' % (self.folder_name, self.save_right), img_right)
            self.save_right += -1
            self.lock.release()
        except uvclite.UVCError as e:
          logging.debug(e)
        except cv2.error as e:
          logging.debug(e)

  def start_capturing(self, sync=False):
    self.left_thread = threading.Thread(
        name='Carama izquierda', target=self.run_left)
    self.left_thread.start()

    self.right_thread = threading.Thread(
        name="Camara derecha", target=self.run_right)
    self.right_thread.start()

  def stop_capturing(self):
    self.is_left_capturing = False
    self.is_right_capturing = False

  def save_folder(self):
  	self.folder_name = sg.PopupGetText('Select a folder name')
  	self.folder_name += '/'
  	if self.folder_name == '/':
  		self.folder_name = ''

  	if self.folder_name != '':
  		logging.debug('creating folder: %s' % self.folder_name)	
  		os.mkdir(self.folder_name)

  def close(self):
    self.window.Close()

  def save(self, n_imgs):
    if self.is_left_capturing and self.is_right_capturing:
      logging.debug('Guardando %s imagenes' % n_imgs)
      self.n_imgs = n_imgs
      self.save_left = n_imgs
      self.save_right = n_imgs
    else:
      logging.debug('Camaras no estan en modo streaming. No se pueden guardar imagenes')

    self.window2 = sg.Window('Footshot', grab_anywhere=False,
                            icon='Isotipo.ico').Layout(self._capture_layout).Finalize()

  def __del__(self):
    self.close()


def main():
  with uvclite.UVCContext() as context:
    try:
      Y16 = uvclite.libuvc.uvc_frame_format.UVC_FRAME_FORMAT_Y16
      MJPEG = uvclite.libuvc.uvc_frame_format.UVC_FRAME_FORMAT_MJPEG

      cam_IR = Camera(context, 0x1e4e, 0x0100, Y16, 160, 120, 9)
      cam_VIS = Camera(context, 0x046d, 0x082b, MJPEG, 320, 240, 30)

      fg = FootGui(cam_IR, cam_VIS)

      loop = True
      while loop:
        event, values = fg.read()
        if event == 'Record':
          fg.start_streaming()
          fg.start_capturing()
        if event == 'Stop':
          fg.stop_capturing()
          fg.stop_streaming()
        if event == 'Exit':
          loop = False
        if event == 'About':
          fg.save(10)
          continue
        if event == 'New Folder':
          fg.save_folder()		

      fg.stop_capturing()
      fg.stop_streaming()	
      fg.close()
      sys.exit(0)

    except uvclite.UVCError as e:
      logging.debug(e)


if __name__ == '__main__':
  main()
