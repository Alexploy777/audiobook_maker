from PyQt5.QtCore import QObject, pyqtSignal


class ConverterSignals(QObject):
    progress_bar_signal = pyqtSignal(int)
    label_info_signal = pyqtSignal(str)
    label_info_signal_2 = pyqtSignal(str)
    all_tasks_completed = pyqtSignal()  # Сигнал о завершении всех заданий
    all_tasks_complete = pyqtSignal()  # Сигнал об окончании объединения
