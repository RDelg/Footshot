import PySimpleGUI27 as sg
import numpy as np
import cv2
import uvclite

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
    device_IR = context.find_device(0x1e4e, 0x0100) # finds PureThermal cam
    device_VIS = context.find_device(0x046d, 0x082b) # finds Vis device

    device_IR.open()
    device_VIS.open()

    device_IR.set_stream_format(uvc_frame_format.UVC_FRAME_FORMAT_Y16, 160, 120, 9)  
    device_VIS.set_stream_format(uvc_frame_format.UVC_FRAME_FORMAT_MJPEG, 320, 240, 30)

    device_IR.start_streaming()
    device_VIS.start_streaming()

    while capturing:
        try:
            frame_IR = device_IR.get_frame(0)
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