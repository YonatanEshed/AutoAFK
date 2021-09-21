from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

import time
import threading
import sys
import keyboard

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon


class AppWin(QWidget):

    keyboard = KeyboardController()
    mouse = MouseController()

    def __init__(self):
        super().__init__()
        loadUi('AutoAFK.ui', self)
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle('AutoAFK')

        self.available = False

        # set default key binds
        with open('keybind.txt', 'r') as f:
            key_binds = f.readlines()[0].split(', ')
            self.start_key_bind = key_binds[0]
            self.stop_key_bind = key_binds[1]
            self.start_key_bind_btn.setText(self.start_key_bind)
            self.stop_key_bind_btn.setText(self.stop_key_bind)

        # set start and stop buttons
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)

        # switch windows buttons
        self.settings_btn.clicked.connect(self.switch_to_settings)
        self.back_btn.clicked.connect(self.switch_to_main_win)

        self.on_press_label.setHidden(True)

        # set key bind button
        self.start_key_bind_btn.clicked.connect(lambda: self.get_key_bind('start'))
        self.stop_key_bind_btn.clicked.connect(lambda: self.get_key_bind('stop'))

        # start getting key binds
        self.hook = keyboard.on_press(self.hot_keys)

    def switch_to_settings(self):
        keyboard.unhook(self.hook)
        self.Windows.setCurrentIndex(1)

    def switch_to_main_win(self):
        self.error_label.setText('')

        # rewrite key bind in the file
        with open('keybind.txt', 'w') as f:
            f.write(f'{self.start_key_bind}, {self.stop_key_bind}')

        self.hook = keyboard.on_press(self.hot_keys)
        self.Windows.setCurrentIndex(0)

    def start(self):
        self.available = True

        # start threading
        start_afk = threading.Thread(target=self.run)
        start_afk.start()

    def stop(self):
        # stop the threading
        self.available = False

    def run(self):
        time.sleep(2)

        # start processing
        while self.available:

            # move the character
            for step in 'a' * 5 + 'w' * 5 + 'd' * 5 + 's' * 5:
                if not self.available:
                    break
                self.keyboard.press(str(step))
                time.sleep(0.14)
                self.keyboard.release(str(step))

            # shoot
            for _ in range(5):
                if not self.available:
                    break
                self.mouse.click(Button.left)
                time.sleep(.14)

            # reload
            if self.available:
                self.keyboard.press('r')
                time.sleep(.14)
                self.keyboard.release('r')

    def hot_keys(self, event):

        # check start key bind
        if (event.name == self.start_key_bind):
            self.available = True
            self.start()

        # check stop key bind
        elif event.name == self.stop_key_bind:
            self.available = False

    def get_key_bind(self, name):
        self.on_press_label.setHidden(False)

        if name == 'start':
            self.changes_hook = keyboard.on_press(self.set_start_key_bind)
        if name == 'stop':
            self.changes_hook = keyboard.on_press(self.set_stop_key_bind)

    def set_start_key_bind(self, event):
        if event.name and event.name != self.stop_key_bind:
            # set start key bind
            self.start_key_bind = event.name
            self.start_key_bind_btn.setText(self.start_key_bind)

            keyboard.unhook(self.changes_hook)
            self.on_press_label.setHidden(True)

        elif event.name == self.stop_key_bind:
            self.error_label.setText('You can not put one key for both actions')
            keyboard.unhook(self.changes_hook)
            self.on_press_label.setHidden(True)

    def set_stop_key_bind(self, event):
        if event.name and event.name != self.start_key_bind:
            # set stop key bind
            self.stop_key_bind = event.name
            self.stop_key_bind_btn.setText(self.stop_key_bind)

            # rewrite key bind in the file
            keyboard.unhook(self.changes_hook)
            self.on_press_label.setHidden(True)

        elif event.name == self.start_key_bind:
            self.error_label.setText('You can not put one key for both actions')
            keyboard.unhook(self.changes_hook)
            self.on_press_label.setHidden(True)


def main():
    # run the application
    app = QApplication(sys.argv)
    win = AppWin()
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
