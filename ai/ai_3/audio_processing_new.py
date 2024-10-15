# audio_processing_new.py
import os
import subprocess
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot, QObject, pyqtSignal, QMetaObject, Qt, Q_ARG
from pydub import AudioSegment
from io import BytesIO
from time import time
import tempfile

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class ConverterSignals(QObject):
    progress_bar_signal = pyqtSignal(int)  # Сигнал progressBar


class Converter(QRunnable):
    def __init__(self, input_path, output_temp_files_list, index, total_files):
        super().__init__()
        self.input_path = input_path
        self.output_temp_files_list = output_temp_files_list
        self.index = index
        self.my_signals = ConverterSignals()

    @pyqtSlot()
    def run(self):
        output_file = self.convert_mp3_to_m4b(self.input_path)
        self.output_temp_files_list[self.index] = output_file  # Запись результата по индексу

        # Излучаем сигнал для обновления прогресс-бара
        # self.signals.progress_bar_signal.emit(self.progress)
        # print(f"Прогресс: {self.progress}%")

    def convert_mp3_to_m4b(self, input_path):
        try:
            audio = AudioSegment.from_mp3(input_path)
            output_buffer = tempfile.NamedTemporaryFile(suffix='.m4b', delete=False)  # Создаем временный файл
            audio.export(output_buffer.name, format="mp4", codec="aac")
            output_buffer.close()  # Явно закрываем временный файл
            print(f"Файл успешно конвертирован: {input_path}")
            self.my_signals.progress_bar_signal.emit(self.index)
            return output_buffer

        except Exception as e:
            print(f"Ошибка при конвертации файла {input_path}: {e}")
            return None


# class ConverterManager(QObject):
class ConverterManager():
    def __init__(self, progressBar):
        super().__init__()
        self.progressBar = progressBar
        self.progressBar.setValue(0)

        self.thread_pool = QThreadPool()  # объект пула потоков

        self.output_temp_files_list = []  # Список для хранения временных файлов аудиофайлов
        self.total_converted_files = 0  # Количество сконвертированных файлов

    def update_progress(self, task_num):
        """Обновляет прогрессбар на основании выполнения задач."""
        self.total_converted_files += 1  # Увеличиваем количество сконвертированных файлов
        progress_percentage = int(self.total_converted_files * 100 / self.total_files)  # Рассчитываем процент
        print(progress_percentage)
        self.progressBar.setValue(progress_percentage)

    def start(self, input_list, output_file):
        self.output_temp_files_list = [None] * len(input_list)  # Инициализируем список с None для каждого файла
        self.total_files = len(input_list)  # общее число исходных mp3 файлов

        self.total_converted_files = 0  # Сбрасываем счетчик сконвертированных файлов
        self.progressBar.setValue(0)  # Сбрасываем прогрессбар

        # Запускаем задачи
        for index, file in enumerate(input_list):
            converter = Converter(file, self.output_temp_files_list, index, self.total_files)
            converter.my_signals.progress_bar_signal.connect(self.update_progress)
            self.thread_pool.start(converter)

        # Ждём завершения всех потоков
        # self.thread_pool.waitForDone()
        # print('Начинаем объединять файлы..')
        # print(self.output_temp_files_list)

        # Если все задачи завершены, отправляем сигнал

        # Ждём завершения всех потоков
        # self.thread_pool.waitForDone()

        # temp_files_list = self.output_temp_files_list
        # merger = M4BMerger(temp_files_list, output_file)
        # merger.run()
        #
        # # Удаление временных файлов после объединения
        # for temp_file in temp_files_list:
        #     if temp_file:
        #         temp_file.close()  # Явно закрываем временный файл
        #         os.remove(temp_file.name)  # Удаляем временный файл


if __name__ == '__main__':
    pass
    input_list = ['mp3/1.mp3', 'mp3/2.mp3']
    output_file = 'final.m4b'
    # start_time = time()
    converter_manager = ConverterManager()
    converter_manager.start(input_list, output_file)
    # print('Работа завершена!')
    # print(time() - start_time)
