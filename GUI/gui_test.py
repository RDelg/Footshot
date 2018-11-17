import logging
import threading
import PySimpleGUI as sg

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


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

  _layout2 = [
      [
          sg.Frame('Infrarrojo', _left_frame,
                   font='Any 12', title_color='blue'),
          sg.Frame('Visible', _right_frame,
                   font='Any 12', title_color='blue'),
          sg.Frame('Ultravioleta', _right_frame,
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

  _capture_layout = [[sg.Text('A custom progress meter')],
                     [sg.ProgressBar(10000, orientation='h',
                                     size=(20, 20), key='progressbar')],
                     [sg.Cancel()]]

  def __init__(self):
    self.window = sg.Window('Footshot', grab_anywhere=True,
                            icon='Isotipo.ico').Layout(self._layout)

  def read(self, timeout=None):
    return self.window.Read(timeout)

  def update_left(self, img_left):
    self.window.FindElement('infrarrojo').Update(data=img_left)

  def update_right(self, img_right):
    self.window.FindElement('visual').Update(data=img_right)

  def close(self):
    self.window.Close()

  def change(self):
    self.window2 = sg.Window('Footshot tomando imagenes', grab_anywhere=True,
                          icon='Isotipo.ico', location=(10, 10)).Layout(self._capture_layout).Finalize()

  def __del__(self):
    self.close()


def main():
  fg = FootGui()
  loop = True
  while loop:
    event, values = fg.read()
    if event == 'Exit':
      loop = False
    if event == 'Record':
      fg.change()
    if event == 'About':
      continue
    if event == 'Stop':
      continue
  fg.close()


if __name__ == '__main__':
  main()
