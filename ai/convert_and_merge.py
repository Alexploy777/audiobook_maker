import os
import subprocess
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot, QObject, pyqtSignal
from pydub import AudioSegment
from time import time

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class M4BMerger:
    def __init__(self, input_files, output_file):
        self.input_files = input_files  # Список m4b файлов
        self.output_file = output_file  # Финальный выходной файл
        self.list_file = 'files.txt'  # Временный файл со списком входных файлов

    def create_file_list(self):
        """Создаем временный файл со списком входных m4b файлов."""
        with open(self.list_file, 'w') as f:
            for file in self.input_files:
                f.write(f"file '{file}'\n")

    def merge_files(self):
        """Объединяем m4b файлы с помощью ffmpeg."""
        command = [
            'ffmpeg',
            '-f', 'concat',  # формат ввода: список файлов
            '-safe', '0',  # разрешаем использовать небезопасные символы в путях
            '-i', self.list_file,  # вводим файл со списком
            '-c', 'copy',  # копируем содержимое без перекодирования
            '-y',  # перезаписываем выходной файл без предупреждения
            self.output_file  # выходной файл
        ]

        try:
            # Запускаем процесс ffmpeg
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f'Файлы успешно объединены в {self.output_file}')
        except subprocess.CalledProcessError as e:
            print(f'Ошибка при объединении файлов: {e}')

    def clean_up(self):
        """Удаляем временные файлы."""
        if os.path.exists(self.list_file):
            os.remove(self.list_file)

    def run(self):
        """Основной метод для выполнения всех шагов."""
        self.create_file_list()
        self.merge_files()
        self.clean_up()


class Converter(QRunnable):
    def __init__(self, file, output_temp_file, output_temp_files_list, index):
        super().__init__()
        self.input_path = file
        self.output_temp_file = output_temp_file
        self.output_temp_files_list = output_temp_files_list
        self.index = index

    @pyqtSlot()
    def run(self):
        output_file = self.convert_mp3_to_m4b(self.input_path, self.output_temp_file)
        self.output_temp_files_list[self.index] = output_file  # Запись результата по индексу

    def convert_mp3_to_m4b(self, input_path, output_path):
        try:
            audio = AudioSegment.from_mp3(input_path)
            audio.export(output_path, format="mp4", codec="aac")
            print(f"Файл успешно конвертирован: {output_path}")
            return output_path
        except Exception as e:
            print(f"Ошибка при конвертации файла {input_path}: {e}")
            return None


class ConverterManager(QObject):
    def __init__(self, output_dir_name):
        super().__init__()
        self.output_dir_name = output_dir_name
        self.thread_pool = QThreadPool()
        self.output_temp_files_list = []  # Список для хранения путей к выходным файлам

    def get_output_file_path(self, input_path):
        temp = os.path.abspath(input_path)
        dir_name = os.path.dirname(os.path.dirname(temp))
        full_output_dir = os.path.join(dir_name, self.output_dir_name)
        os.makedirs(full_output_dir, exist_ok=True)
        name = os.path.basename(temp).split(os.extsep)[0]
        output_name = os.path.join(str(full_output_dir), name + '.m4b')
        return output_name

    def del_temp_m4b_files(self, temp_files_list):
        for temp_file in temp_files_list:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def start(self, input_list, output_file):
        self.output_temp_files_list = [None] * len(input_list)  # Инициализируем список с None для каждого файла

        for index, file in enumerate(input_list):
            output_temp_file = self.get_output_file_path(file)
            converter = Converter(file, output_temp_file, self.output_temp_files_list, index)
            self.thread_pool.start(converter)

        # Ждём завершения всех потоков
        self.thread_pool.waitForDone()

        print('Начинаем объединять файлы..')

        temp_files_list = self.output_temp_files_list
        merger = M4BMerger(temp_files_list, output_file)
        merger.run()

        self.del_temp_m4b_files(temp_files_list)


if __name__ == '__main__':
    input_list = ['mp3/1.mp3', 'mp3/2.mp3', 'mp3/3.mp3', 'mp3/4.mp3']
    output_dir_name = 'temp'
    output_file = 'final.m4b'
    start_time = time()
    converter_manager = ConverterManager(output_dir_name)
    converter_manager.start(input_list, output_file)
    print('Работа завершена!')
    print(time() - start_time)
