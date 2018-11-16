import threading

import cv2
import numpy as np

import uvclite
import PySimpleGUI27 as sg


class Camera(object):

  _Y16 = uvclite.libuvc.uvc_frame_format.UVC_FRAME_FORMAT_Y16

  def __init__(self, context, vendor_id=0, product_id=0, frame_format=_Y16, width=160, height=120, frame_rate=9):
    self.context = context
    self.find_device(vendor_id, product_id)
    self.device.open()
    self.set_stream_format(frame_format, width, height, frame_rate)
    self.is_streaming = False

  def find_device(self, vendor_id, product_id):
    self.device = self.context.find_device(vendor_id, product_id)

  def set_stream_format(self, frame_format, width, height, frame_rate):
    self.frame_format = frame_format
    self.width = width
    self.height = height
    self.frame_rate = frame_rate
    self.device.set_stream_format(frame_format, width, height, frame_rate)

  def start_streaming(self):
    if not self.is_streaming:
      self.device.start_streaming()
      self.is_streaming = True

  def stop_streaming(self):
    if self.is_streaming:
      self.device.stop_streaming()
      self.is_streaming = False

  def get_frame(self, timeout):
    assert self.is_streaming, "La camara no esta en modo streaming"
    return self.device.get_frame(timeout)

  def get_img_raw(self, timeout, size=(320, 240)):
    frame = self.get_frame(timeout)
    if frame.size != (2*self.height*self.width):
      return None
    data = np.frombuffer(frame.data, dtype=np.uint16).reshape(
        self.height, self.width)
    if self.width != size[0] or self.height != size[1]:
      data = cv2.resize(data, size)
    cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(data, 8, data)
    img = cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)
    return cv2.imencode('.png', img)[1].tobytes()

  def get_img_jpg(self, timeout, size=(320, 240)):
    frame = self.get_frame(timeout)
    data = np.frombuffer(frame.data, dtype=np.uint16)
    if self.width != size[0] or self.height != size[1]:
      data = cv2.resize(data, size)
    img = cv2.imdecode(data, 1)
    return cv2.imencode('.png', img)[1].tobytes()

  # def __del__(self):
  #   if self.is_streaming:
  #     self.device.stop_streaming()
  #     self.is_streaming == False
  #   self.device.close()


class FootGui(object):

  _left_frame = [
      [sg.T('Text inside of a frame')],
      [sg.CB('Check 1'), sg.CB('Check 2')],
      [sg.Image(data='', background_color='gray', size=(
          320, 240), key='infrarrojo', tooltip='Imagen IR')]
  ]
  _right_frame = [
      [sg.T('Text inside of a frame')],
      [sg.CB('Check 1'), sg.CB('Check 2')],
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
          sg.Button('About', size=(5, 1), font='Any 14')
      ],
      [
          sg.T(' ' * 10)
      ]
  ]

  def __init__(self, left_dev, right_dev):
    self.window = sg.Window('Footshot', grab_anywhere=True,
                            icon='Isotipo.ico').Layout(self._layout)
    self.left_dev = left_dev
    self.right_dev = right_dev
    self.is_left_capturing = False
    self.is_right_capturing = False

  def start_streaming(self):
    if not self.left_dev.is_streaming and not self.left_dev.is_streaming:
      self.left_dev.start_streaming()
      self.right_dev.start_streaming()

  def stop_streaming(self):
    if self.left_dev.is_streaming and self.left_dev.is_streaming:
      self.left_dev.stop_streaming()
      self.right_dev.stop_streaming()

  def read(self, timeout=None):
    return self.window.Read(timeout)

  def update_left(self, img_left):
    self.window.FindElement('infrarrojo').Update(data=img_left)

  def update_right(self, img_right):
    self.window.FindElement('visual').Update(data=img_right)

  def run_left(self):
    if not self.is_left_capturing:
      self.is_left_capturing = True
      while self.is_left_capturing and self.left_dev.is_streaming:
        try:
          left_img = self.left_dev.get_img_raw(0)
          self.update_left(left_img)
        except uvclite.UVCError as e:
          print(e)

  def run_right(self):
    if not self.is_right_capturing:
      self.is_right_capturing = True
      while self.is_right_capturing and self.right_dev.is_streaming:
        try:
          right_img = self.right_dev.get_img_jpg(0)
          self.update_right(right_img)
        except uvclite.UVCError as e:
          print(e)

  def run(self):
    if not self.is_left_capturing:
      self.left_thread = threading.Thread(target=self.run_left)
      self.left_thread.start()

    if not self.is_right_capturing:
      self.right_thread = threading.Thread(target=self.run_right)
      self.right_thread.start()

  def close(self):
    self.window.Close()

  def __del__(self):
    self.window.Close()


def main():
  with uvclite.UVCContext() as context:
    Y16 = uvclite.libuvc.uvc_frame_format.UVC_FRAME_FORMAT_Y16
    MJPEG = uvclite.libuvc.uvc_frame_format.UVC_FRAME_FORMAT_MJPEG

    cam_IR = Camera(context, 0x1e4e, 0x0100, Y16, 160, 120, 9)
    cam_VIS = Camera(context, 0x046d, 0x082b, MJPEG, 320, 240, 30)

    fg = FootGui(cam_IR, cam_VIS)

    loop = True
    while loop:
      print("a")
      event, values = fg.read()

      if event == 'Exit':
        loop = False
      if event == 'Record':
        fg.start_streaming()
        fg.run()
      if event == 'About':
        continue
      if event == 'Stop':
        fg.is_left_capturing = False
        fg.is_right_capturing = False
        fg.stop_streaming()

    fg.close()


if __name__ == '__main__':
  main()
