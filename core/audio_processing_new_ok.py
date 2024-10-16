import sys
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from pydub import AudioSegment
import tempfile
import os



os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class ConverterManager(QObject):
    def __init__(self, audiobook_interface):
        super(ConverterManager, self).__init__()
        print('мы тут!!!!!!!!!!!')
        # self.audiobook_interface = audiobook_interface
        self.progressBar = audiobook_interface.progressBar
        self.label_progress_description = audiobook_interface.label_progress_description
        self.progressBar.setValue(0)
        self.thread_pool = QThreadPool()
        self.completed_tasks = 0  # Количество завершённых задач

        self.output_temp_files_list = []  # Список для хранения временных файлов аудиофайлов

        # Дополнительный сигнал завершения всех задач
        self.all_tasks_completed_signal = ConverterSignals()
        self.all_tasks_completed_signal.all_tasks_completed.connect(self.on_all_tasks_completed)

    # Кнопка для старта задач
    def start_my_task(self, input_list):
        """Запускает выполнение задач в пуле потоков."""
        self.completed_tasks = 0  # Сбрасываем счетчик выполненных задач
        self.progressBar.setValue(0)  # Сбрасываем прогрессбар
        self.quantity = len(input_list)
        self.output_temp_files_list = [None] * self.quantity  # Инициализируем список с None для каждого файла

        # Запускаем задачи
        for index, file in enumerate(input_list):
            some_task = Converter(index=index, quantity=self.quantity, file=file,
                                  output_temp_files_list=self.output_temp_files_list)
            some_task.my_signals.progress_bar_signal.connect(self.update_progress)
            some_task.my_signals.label_info_signal.connect(self.update_label)
            self.thread_pool.start(some_task)

    def update_label(self, value):
        self.label_progress_description.setText(value)


    def update_progress(self, v):
        """Обновляет прогрессбар на основании выполнения задач."""
        self.completed_tasks += 1  # Увеличиваем количество завершённых задач
        progress_percentage = int((self.completed_tasks / self.quantity) * 100)  # Рассчитываем процент
        self.progressBar.setValue(progress_percentage)

        # Если все задачи завершены, отправляем сигнал
        if self.completed_tasks == self.quantity:
            self.all_tasks_completed_signal.all_tasks_completed.emit()

    def on_all_tasks_completed(self):
        """Вызывается при завершении всех задач."""
        temp_files_list = [f.name for f in self.output_temp_files_list]
        print(temp_files_list)
        QMessageBox.information(None, "Завершено", "Все задания выполнены!")
        self.delete_temp_files(temp_files_list)

    def delete_temp_files(self, temp_files_list):
        for temp_file in temp_files_list:
            if temp_file:
                os.remove(temp_file)  # Удаляем временный файл


class ConverterSignals(QObject):
    progress_bar_signal = pyqtSignal(int)
    label_info_signal = pyqtSignal(str)
    all_tasks_completed = pyqtSignal()  # Сигнал о завершении всех заданий


class Converter(QRunnable):
    def __init__(self, index, quantity, file, output_temp_files_list):
        super().__init__()
        self.index = index
        self.quantity = quantity
        self.my_signals = ConverterSignals()
        self.file = file
        self.output_temp_files_list = output_temp_files_list

    @pyqtSlot()
    def run(self):
        """Запускает выполнение задания."""
        output_file = self.convert_mp3_to_m4b(self.file)
        self.output_temp_files_list[self.index] = output_file
        self.my_signals.progress_bar_signal.emit(self.index)  # Отправляем сигнал о завершении задания
        self.my_signals.label_info_signal.emit(f'конвертирую: {os.path.abspath(self.file)}')

    def convert_mp3_to_m4b(self, input_path):
        try:
            audio = AudioSegment.from_mp3(input_path)
            output_buffer = tempfile.NamedTemporaryFile(suffix='.m4b', delete=False)  # Создаем временный файл
            audio.export(output_buffer.name, format="mp4", codec="aac")
            output_buffer.close()  # Явно закрываем временный файл
            print(f"Файл успешно конвертирован: {input_path}")
            return output_buffer

        except Exception as e:
            print(f"Ошибка при конвертации файла {input_path}: {e}")
            return None


