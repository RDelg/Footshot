import PySimpleGUI as sg
import numpy as np
import cv2

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


window = sg.Window('Footshot', grab_anywhere=True, icon= 'Isotipo.ico').Layout(layout)

while True:
  event, values = window.Read()  
  print(event, values)
  if event is None or event == 'Exit':  
      break  
  if event == 'Show':  
      # change the "output" element to be the value of "input" element  
      window.FindElement('_OUTPUT_').Update(values['_IN_'])


# img = np.full((480, 640),255)
# imgbytes=cv2.imencode('.png', img)[1].tobytes() #this is faster, shorter and needs less includes
# window.FindElement('image2').Update(data=imgbytes)
# sg.Popup(event, values, line_width=200)

window.Close()