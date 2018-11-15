import cv2
import numpy as np
import PySimpleGUI as sg

class FootGui(object):

  _left_frame = [      
                  [sg.T('Text inside of a frame')],      
                  [sg.CB('Check 1'), sg.CB('Check 2')],
                  [sg.Image(filename='infrarrojo.png', background_color='gray', size=(640, 480), key='infrarrojo', tooltip ='Imagen IR')]      
                ]
  _right_frame =  [      
                    [sg.T('Text inside of a frame')],      
                    [sg.CB('Check 1'), sg.CB('Check 2')],
                    [sg.Image(filename='visual.png', background_color='green', size=(640, 480), key='visual', tooltip ='Imagen Visual')]      
                  ]
  _layout = [
              [
                sg.Frame('Infrarrojo', _left_frame, font='Any 12', title_color='blue'),
                sg.Frame('Visible', _right_frame, font='Any 12', title_color='blue')
              ],
              [
                sg.T(' '  * 50),
                sg.Button('Record', size=(20, 1), font='Helvetica 14'),
                sg.Button('Stop', size=(20, 1), font='Any 14'),
                sg.Button('Exit', size=(20, 1), font='Helvetica 14'),
                sg.Button('About', size=(20,1), font='Any 14')
              ],
              [
                sg.T(' '  * 10)
              ]
            ]

  def __init__(self):
    self.window = sg.Window('Footshot', grab_anywhere=True, icon= 'Isotipo.ico').Layout(self._layout)

  def read(self):
    return self.window.Read()

  def update_img(self, img_left, img_right):
    window.FindElement('infrarrojo').Update(data=img_left)
    window.FindElement('visual').Update(data=img_right)

  def __del__(self):
    self.window.Close()


def main():
  fg = FootGui()
  while True:
    event, values = fg.read()
    if event == 'Exit':
      break


if __name__ == '__main__':
  main()