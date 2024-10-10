import os
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot, QObject
from pydub import AudioSegment
from io import BytesIO
from time import time

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class M4BMerger:
    def __init__(self, input_files, output_file):
        self.input_files = input_files  # Список буферов аудиофайлов
        self.output_file = output_file  # Финальный выходной файл

    def merge_files(self):
        """Объединяем m4b файлы в один с помощью pydub."""
        merged_audio = AudioSegment.empty()

        for file_data in self.input_files:
            if file_data:
                file_data.seek(0)  # Сбрасываем указатель потока в начало
                audio = AudioSegment.from_file(file_data, format="mp4")
                merged_audio += audio  # Объединяем аудио файлы

        # Экспортируем объединённый аудиофайл в выходной файл
        merged_audio.export(self.output_file, format="mp4", codec="aac")
        print(f'Файлы успешно объединены в {self.output_file}')

    def run(self):
        """Основной метод для выполнения всех шагов."""
        self.merge_files()


class Converter(QRunnable):
    def __init__(self, file, output_temp_files_list, index):
        super().__init__()
        self.input_path = file
        self.output_temp_files_list = output_temp_files_list
        self.index = index

    @pyqtSlot()
    def run(self):
        output_file = self.convert_mp3_to_m4b(self.input_path)
        self.output_temp_files_list[self.index] = output_file  # Запись результата по индексу

    def convert_mp3_to_m4b(self, input_path):
        try:
            audio = AudioSegment.from_mp3(input_path)
            output_buffer = BytesIO()
            audio.export(output_buffer, format="mp4", codec="aac")
            print(f"Файл успешно конвертирован в буфер: {input_path}")
            return output_buffer
        except Exception as e:
            print(f"Ошибка при конвертации файла {input_path}: {e}")
            return None


class ConverterManager(QObject):
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()
        self.output_temp_files_list = []  # Список для хранения аудиобуферов

    def start(self, input_list, output_file):
        self.output_temp_files_list = [None] * len(input_list)  # Инициализируем список с None для каждого файла

        for index, file in enumerate(input_list):
            converter = Converter(file, self.output_temp_files_list, index)
            self.thread_pool.start(converter)

        # Ждём завершения всех потоков
        self.thread_pool.waitForDone()

        print('Начинаем объединять файлы..')

        temp_files_list = self.output_temp_files_list
        merger = M4BMerger(temp_files_list, output_file)
        merger.run()


if __name__ == '__main__':
    input_list = ['mp3/1.mp3', 'mp3/2.mp3', 'mp3/3.mp3', 'mp3/4.mp3']
    output_file = 'final.m4b'
    start_time = time()
    converter_manager = ConverterManager()
    converter_manager.start(input_list, output_file)
    print('Работа завершена!')
    print(time() - start_time)
