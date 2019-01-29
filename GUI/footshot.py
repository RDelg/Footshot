import logging
import threading
import requests
import sys
import os
from time import sleep

import cv2
import numpy as np
from Utils.aws_send import Foot_AWS

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

    #should return a 16bits grayscale denormalized img  
    def get_raw_frame(self, timeout, size=(320, 240)):
        frame = self._get_frame(timeout)
        while frame.size != (2*self.height * self.width):
            frame = self._get_frame(timeout)

        img_data = np.frombuffer(frame.data, dtype=np.uint16).reshape(
            self.height, self.width)

        if self.width != size[0] or self.height != size[1]:
            img_data = cv2.resize(img_data, size)

        return img_data   

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

#showing the picture vs saving the full INFRA not normalized
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
                    sg.Button('New Folder', size=(7, 1), font='Helvetica 14'),
                    sg.Button('Capture', size=(5, 1), font='Any 14'),
                    sg.Button('Analyze', size=(5, 1), font='Helvetica 14'),
                    sg.Button('Exit', size=(5, 1), font='Helvetica 14')
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
        rows, cols = img_left.shape[:2]
        M = cv2.getRotationMatrix2D((cols/2,rows/2), 180, 1)
        img_left_rotated = cv2.warpAffine(img_left, M, (cols, rows))
        #done
        img_color = cv2.applyColorMap(img_left_rotated, cv2.COLORMAP_JET)

        self.img_left = cv2.imencode('.png', img_color)[1]
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
                    img_left_raw = self.left_dev.get_raw_frame(0) 
                    self.update_left(img_left)
                    # Guardando imagen
                    if self.save_left > 0:
                        self.lock.acquire()
                        logging.debug('Guardando imagen %s' % self.save_left)
                        self.left_dev.imwrite('%sIR_%s.png' % (self.folder_name, self.save_left), img_left_raw)

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
        self.left_thread.join()
        self.right_thread.join()

    def save_folder(self):
        self.folder_name = sg.PopupGetText('Select a folder name')
        if self.folder_name == '' or self.folder_name is None:
            self.folder_name = ''

        if self.folder_name != '':
            self.folder_name += '/'
            logging.debug('creating folder: %s' % self.folder_name)
            try:    
                os.mkdir(self.folder_name)
            except OSError:
                print('La carpeta ya existe, sera seleccionada.')   

    def close(self):
        self.window.Close()

    def upload_files(self):
        #call from utils the functions
        files = os.listdir(self.folder_name)
        aws = Foot_AWS()

        if aws.connected == False:
            self.window3 = sg.Popup('Error', 'No hay conexion a internet.')
            return

        for file in files:
            aws.upload_file(self.folder_name + file)
            
        data = {
            'rut': '19073061-1',
            'imagenes': self.folder_name
        }   
        requests.post('http://192.168.1.46:8000/api/tests/record', data)    


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
    login = sg.Window('Ingrese').Layout([
                        [sg.Text('Ingrese a Footshot')],      
                        [sg.Text('RUT', size=(15, 1)), sg.InputText('rut', key='rut')],      
                        [sg.Text('PIN', size=(15, 1)), sg.InputText('pass', key='pass', password_char='*')], 
                        [sg.Submit(), sg.Cancel()]
                        ])

    failed = False
    while True:
        event, values = login.Read()
        if event == 'Cancel' or event is None:
            failed = True
            break
        elif event == 'Submit':
            print(values)
            break

    if failed: sys.exit(0)
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
                if event == 'Exit' or values is None:
                    logging.debug('Closing app')
                    fg.stop_capturing()
                    fg.stop_streaming()     
                    loop = False
                if event == 'Capture':
                    fg.save(5)
                    continue
                if event == 'New Folder':
                    fg.save_folder()
                if event == 'Save':
                    fg.upload_files()       

            sleep(1)
            fg.close()
            sys.exit(0)

        except uvclite.UVCError as e:
            logging.debug(e)


if __name__ == '__main__':
    main()
