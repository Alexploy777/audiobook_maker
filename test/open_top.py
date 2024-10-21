import sys
import os
import subprocess
import time
import win32gui
import win32con
import ctypes
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class FileOpenerApp(QWidget):
    def __init__(self, file_path):
        super().__init__()

        self.file_path = file_path
        self.initUI()

    def initUI(self):
        # Создаем кнопку
        self.button = QPushButton('Открыть папку с файлом', self)
        self.button.clicked.connect(self.open_folder_with_file)

        # Вертикальный layout для кнопки
        layout = QVBoxLayout()
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setWindowTitle('Открытие папки с файлом')
        self.show()

    def open_folder_with_file(self):
        folder_path = os.path.dirname(self.file_path)

        if sys.platform == "win32":
            # Правильный формат пути для Windows
            normalized_path = os.path.normpath(self.file_path)
            subprocess.Popen(f'explorer /select,\"{normalized_path}\"')

            # Ожидание открытия проводника
            time.sleep(0.5)

            # Получаем PID (идентификатор процесса) проводника
            explorer_hwnd = None

            def enum_window_callback(hwnd, _):
                nonlocal explorer_hwnd
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "explorer" in title.lower():
                        explorer_hwnd = hwnd
                        return False  # Останавливаем поиск, как только найден проводник

            win32gui.EnumWindows(enum_window_callback, None)

            if explorer_hwnd:
                # Разрешаем текущему процессу фокусировать проводник
                ctypes.windll.user32.AllowSetForegroundWindow(ctypes.windll.kernel32.GetCurrentProcessId())

                # Поднимаем окно проводника на передний план
                ctypes.windll.user32.SetForegroundWindow(explorer_hwnd)

                # Делаем проводник окном "поверх всех"
                win32gui.SetWindowPos(
                    explorer_hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                )

                # Снимаем флаг "поверх всех", чтобы проводник вел себя нормально
                win32gui.SetWindowPos(
                    explorer_hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                )

        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", self.file_path])
        else:
            subprocess.Popen(["xdg-open", folder_path])


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Задаем абсолютный путь к файлу
    file_path = r"D:\CODING\audiobook_maker\mp3\Лю Цысинь-sss.m4b"

    ex = FileOpenerApp(file_path)
    sys.exit(app.exec_())
