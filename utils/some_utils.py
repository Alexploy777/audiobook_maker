from PyQt5.QtCore import QTime, QTimer


class Timer:
    def __init__(self, *args):
        self.lcdNumber = args[0]
        self.time = QTime(0, 0, 0)
        self.timer = QTimer()  # Создаем таймер, который будет обновляться каждую секунду
        self.timer.timeout.connect(self.update_time)

    def update_time(self):
        self.time = self.time.addSecs(1)  # Увеличиваем время на 1 секунду
        time_text = self.time.toString("mm.ss")  # Форматируем время в формате MM:SS
        self.lcdNumber.display(time_text)  # Обновляем QLCDNumber

    def start_timer(self):
        self.timer.start(1000)  # Запускаем таймер с обновлением каждую секунду

    def stop_timer(self):
        self.timer.stop()  # Останавливаем таймер

    def reset_timer(self):
        # Останавливаем таймер и сбрасываем время
        self.timer.stop()
        self.time = QTime(0, 0, 0)
        self.lcdNumber.display(self.time.toString("mm.ss"))  # Обновляем отображение на 00:00


import platform
import subprocess

# def run_ffmpeg_command(command):
#     system_type = platform.system()
#     if system_type == 'Windows':
#         startupinfo = subprocess.STARTUPINFO()
#         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
#         startupinfo.wShowWindow = subprocess.SW_HIDE
#         process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
#     else:
#         process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#
#     stdout, stderr = process.communicate()
#     return stdout, stderr
