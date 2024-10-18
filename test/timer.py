import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLCDNumber, QPushButton
from PyQt5.QtCore import QTimer, QTime


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        # Создаем объект времени с началом отсчета
        self.time = QTime(0, 0, 0)

        # Создаем таймер, который будет обновляться каждую секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

    def init_ui(self):
        layout = QVBoxLayout()

        # Добавляем QLCDNumber для отображения времени
        self.lcd = QLCDNumber(self)
        self.lcd.setDigitCount(5)  # Устанавливаем количество цифр (MM:SS)
        layout.addWidget(self.lcd)

        # Кнопка для запуска таймера
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        # Кнопка для остановки таймера
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_timer)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)
        self.setWindowTitle("Timer Example")
        self.show()

    def start_timer(self):
        self.timer.start(1000)  # Запускаем таймер с обновлением каждую секунду

    def stop_timer(self):
        self.timer.stop()  # Останавливаем таймер

    def update_time(self):
        # Увеличиваем время на 1 секунду
        self.time = self.time.addSecs(1)

        # Форматируем время в формате MM:SS
        time_text = self.time.toString("mm.ss")

        # Обновляем QLCDNumber
        self.lcd.display(time_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    sys.exit(app.exec_())
