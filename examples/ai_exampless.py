import sys
import time

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QPushButton, QVBoxLayout, QWidget

class WorkerSignals(QObject):
    progress_signal = pyqtSignal(int)  # Сигнал для обновления прогресс бара

class Worker(QRunnable):
    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        # Здесь выполняется ваша длительная задача
        for i in range(100):
            # Симулируем длительную операцию
            time.sleep(0.1)

            # Отправляем сигнал о прогрессе
            self.signals.progress_signal.emit(i)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.threadpool = QThreadPool()
        print("Multi-threading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.btn = QPushButton('Start')
        self.btn.clicked.connect(self.run)

        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(self.btn)
        layout.addWidget(self.progressBar)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def run(self):
        # Создаем новый рабочий объект
        worker = Worker()
        worker.signals.progress_signal.connect(self.update_progress)
        # Добавляем задачу в пул потоков
        self.threadpool.start(worker)

    def update_progress(self, value):
        self.progressBar.setValue(value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())