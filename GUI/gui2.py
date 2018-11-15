import PySimpleGUI27 as sg
import numpy as np
import cv2
import uvclite
from time import sleep


class Camera(object):

  _frame_format = uvclite.libuvc.uvc_frame_format


  def __init__(self, context, vendor_id=0, product_id=0, frame_format=_frame_format.UVC_FRAME_FORMAT_Y16, width=160, height=120, frame_rate=9):
    """
    
    """
    self.context = context
    self.find_device(vendor_id, product_id)
    self.device.open()
    self.set_stream_format(frame_format, width, height, frame_rate)
    self.is_streaming = False


  def find_device(self, vendor_id, product_id):
    self.device = context.find_device(vendor_id, product_id)


  def set_stream_format(self, frame_format, width, height, frame_rate):
    self.frame_format = frame_format
    self.width = width
    self.height = height
    self.frame_rate = frame_rate
    self.device.set_stream_format(frame_format, width, height, frame_rate)

  
  def start_streaming(self):
    if not self.is_streaming:
      self.device.start_streaming()
      self.start_streaming = True
      print("CAM Streaming")

  
  def stop_streaming(self):
    if self.is_streaming:
      self.device.stop_streaming()
      self.start_streaming = False

  
  def get_frame(self, timeout):
    return self.device.get_frame(timeout) if self.is_streaming else False


  def get_img_raw(self, timeout, size = (320, 240)):
    frame = get_frame(timeout)
    if not frame or frame_IR.size != (2*self.height*self.width):
      return False
    data = np.frombuffer(frame.data, dtype=np.uint16).reshape(self.width, self.height)
    if self.width != size[0] or self.height!= size[1]: 
      data = cv2.resize(data, size)
    cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(data, 8, data)
    img = cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)
    return cv2.imencode('.png', img_)[1].tobytes()


  def get_img_jpg(self, timeout, size = (320, 240)):
    frame = get_frame(timeout)
    if not frame:
      return False
    data = np.frombuffer(frame.data, dtype=np.uint16)
    img = cv2.imdecode(data, 1)
    return cv2.imencode('.png', img)[1].tobytes()


  def __del__(self):
    if self.streaming:
      self.device.stop_streaming()
      self.streaming == False
    device.close()


def raw_to_8bit(data):
   cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
   np.right_shift(data, 8, data)
   return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

frame_layout = [
                  [sg.Image(data='', background_color='gray', size=(320, 240), key='infrarrojo', tooltip ='Imagen IR')]      
               ]

frame_layout2 = [ 
                  [sg.Image(filename='visual.png', background_color='green', size=(320, 240), key='visual', tooltip ='Imagen Visual')]      
                ] 

layout = [
            [
              sg.Frame('Infrarrojo', frame_layout, font='Any 12', title_color='blue'),
              #sg.VerticalSeparator(pad=(0,0)),
              sg.Frame('Visible', frame_layout2, font='Any 12', title_color='blue')
            ],
            [
              sg.T(' '  * 10),
              sg.Button('Record', size=(5, 1), font='Helvetica 10'),
              sg.Button('Stop', size=(5, 1), font='Any 10'),
              sg.Button('Exit', size=(5, 1), font='Helvetica 10'),
              sg.Button('About', size=(5,1), font='Any 10')
            ],
            [
              sg.T(' '  * 10)
            ]
        ]

uvc_frame_format = uvclite.libuvc.uvc_frame_format
capturing = True
window = sg.Window('Footshot', grab_anywhere=True, icon= 'Isotipo.ico').Layout(layout)

with uvclite.UVCContext() as context:
    cam = Camera(context, 0x1e4e, 0x0100)
    device_VIS = context.find_device(0x046d, 0x082b) # finds Vis device

    device_VIS.open()

    device_VIS.set_stream_format(uvc_frame_format.UVC_FRAME_FORMAT_MJPEG, 320, 240, 30)

    device_VIS.start_streaming()
    cam.start_streaming()
    while capturing:
        try:
            frame_IR = cam.get_frame(0)
            frame_VIS = device_VIS.get_frame(0)

            if(frame_IR.size != (2*160*120)): # sometimes the IR webcam doesn't return a fullframe
                continue

            # Convert to numpy object
            data_IR = np.frombuffer(frame_IR.data, dtype=np.uint16).reshape(120, 160)
            data_VIS = np.frombuffer(frame_VIS.data, dtype=np.uint16)

            # Resizes
            data_IR = cv2.resize(data_IR, (320, 240))

            # Decodes
            img_IR = raw_to_8bit(data_IR)
            img_VIS = cv2.imdecode(data_VIS, 1)

            event, values = window.Read(0)

            # Updates
            window.FindElement('infrarrojo').Update(data=cv2.imencode('.png', img_IR)[1].tobytes())
            window.FindElement('visual').Update(data=cv2.imencode('.png', img_VIS)[1].tobytes())

            if event is None or event == 'Exit':  
                capturing = False

        except uvclite.UVCError as e:
            print(e)
            if(e[1] == 110):
                continue
            else:
                break

    device_IR.stop_streaming()
    device_VIS.stop_streaming()
    device_IR.close()
    device_VIS.close()

window.Close()