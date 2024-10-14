import random
import sys
import time
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow

from gui import Ui_MainWindow  # Подключаем ваш интерфейс


class ProgressBar_class(QMainWindow, Ui_MainWindow):
    quantity = 5  # Количество задач

    def __init__(self):
        super(ProgressBar_class, self).__init__()
        self.ui = Ui_MainWindow()
        self.setupUi(self)
        self.setWindowTitle('main_ex.py')
        self.pushButton.clicked.connect(self.start_my_task)  # Кнопка для старта задач
        self.progressBar.setValue(0)
        self.thread_pool = QThreadPool()
        self.completed_tasks = 0  # Количество выполненных задач

    def update_progressbar(self, value):
        """Обновляет прогрессбар по полученному значению."""
        self.progressBar.setValue(value)

    def start_my_task(self):
        """Стартует выполнение задач в пуле потоков."""
        quantity = self.quantity
        self.completed_tasks = 0  # Сбрасываем счетчик выполненных задач
        self.progressBar.setValue(0)  # Сбрасываем прогрессбар
        # thread_pool = QThreadPool()

        for num in range(quantity):
            some_task = MyTask(num, quantity)
            some_task.my_signals.progress_signal.connect(self.update_progress)
            self.thread_pool.start(some_task)

    def update_progress(self, value):
        """Обновляет прогресс-бар на основании выполнения задачи."""
        self.completed_tasks += 1  # Увеличиваем количество выполненных задач
        progress_percentage = int((self.completed_tasks / self.quantity) * 100)  # Рассчитываем процент выполнения
        self.progressBar.setValue(progress_percentage)


class My_signals(QObject):
    progress_signal = pyqtSignal(int)


class MyTask(QRunnable):
    def __init__(self, num, quantity):
        super().__init__()
        self.num = num
        self.quantity = quantity
        self.my_signals = My_signals()

    @pyqtSlot()
    def run(self):
        """Запускает выполнение задания."""
        self.sometask(self.num)

    def sometask(self, num):
        """Задание, которое выполняется с задержкой."""
        print(f'Старт задания номер {num}')
        time.sleep(random.randint(1, 5))  # Имитация работы
        print(f'Стоп задания {num}')
        self.my_signals.progress_signal.emit(1)  # Отправляем сигнал о завершении задания


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ProgressBar_class()
    w.show()
    sys.exit(app.exec_())
