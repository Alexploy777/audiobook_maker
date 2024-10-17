import sys
import time
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject, QMutex
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget


class WorkerSignals(QObject):
    finished = pyqtSignal()


class Worker(QRunnable):
    def __init__(self, stop_flag):
        super().__init__()
        self.stop_flag = stop_flag
        self.signals = WorkerSignals()

    def run(self):
        # Симуляция длительной задачи
        for i in range(10):
            if self.stop_flag[0]:  # Проверка флага прерывания
                print("Процесс остановлен.")
                break
            print(f"Выполняется шаг {i}")
            time.sleep(5)
        self.signals.finished.emit()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()
        self.stop_flag = [False]  # Флаг для остановки задач

        self.start_button = QPushButton("Начать")
        self.stop_button = QPushButton("Остановить")

        self.start_button.clicked.connect(self.start_tasks)
        self.stop_button.clicked.connect(self.stop_tasks)

        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def start_tasks(self):
        self.stop_flag[0] = False  # Сбрасываем флаг остановки

        # Создаём и запускаем несколько потоков
        for _ in range(3):  # Запуск трёх задач
            worker = Worker(self.stop_flag)
            worker.signals.finished.connect(self.task_finished)
            self.threadpool.start(worker)

    def stop_tasks(self):
        self.stop_flag[0] = True  # Устанавливаем флаг остановки

    def task_finished(self):
        print("Задача завершена")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
