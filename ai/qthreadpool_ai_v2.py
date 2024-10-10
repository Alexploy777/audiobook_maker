import os
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot
from pydub import AudioSegment

from ai.my_main import output_file

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class Converter(QRunnable):
    def __init__(self, input_path, output_dir_name, output_list, index):
        super().__init__()
        self.input_path = input_path
        self.output_dir_name = output_dir_name
        self.output_list = output_list
        self.index = index

    @pyqtSlot()
    def run(self):
        output_file = self.convert_mp3_to_m4b(self.input_path)
        self.output_list[self.index] = output_file  # Запись результата по индексу

    def get_output_file_path(self, input_path):
        '''
        Функция формирует и возвращает абсолютный путь временного файла с именем исходного файла
        :param input_path: str
        :return: str
        '''
        temp = os.path.abspath(input_path)
        dir_name = os.path.dirname(os.path.dirname(temp))
        full_output_dir = os.path.join(dir_name, self.output_dir_name)
        os.makedirs(full_output_dir, exist_ok=True)
        name = os.path.basename(temp).split(os.extsep)[0]
        output_name = os.path.join(str(full_output_dir), name + '.m4b')
        return output_name

    def convert_mp3_to_m4b(self, input_path):
        audio = AudioSegment.from_mp3(input_path)
        output_full_path = self.get_output_file_path(input_path)
        audio.export(output_full_path, format="mp4", codec="aac")
        print(f"Файл успешно конвертирован: {output_full_path}")
        return output_full_path


class ConverterManager:
    def __init__(self, output_dir_name):
        self.output_dir_name = output_dir_name
        self.thread_pool = QThreadPool()
        self.output_temp_files = []  # Список для хранения путей к выходным файлам

    def start(self, input_list):
        self.output_temp_files = [None] * len(input_list)  # Инициализируем список с None для каждого файла
        for index, file in enumerate(input_list):
            converter = Converter(file, self.output_dir_name, self.output_temp_files, index)
            self.thread_pool.start(converter)

        # Ждём завершения всех потоков
        self.thread_pool.waitForDone()


class Combine:
    def __init__(self, output_file):
        self.output_file = output_file

    def combine_files(self, temp_files_list):
        combined = AudioSegment.empty()
        for index, file_path in enumerate(temp_files_list):
            audio = AudioSegment.from_file(file_path, format="mp4")
            combined += audio
        combined.export(self.output_file, format="mp4", codec="aac")

        for temp_file in temp_files_list:
            os.remove(temp_file)


if __name__ == '__main__':
    input_list = ['mp3/1.mp3', 'mp3/2.mp3', 'mp3/3.mp3', 'mp3/4.mp3']
    output_dir_name = 'temp'
    output_file = 'final.m4b'

    converter_manager = ConverterManager(output_dir_name)
    converter_manager.start(input_list)
    temp_files_list = converter_manager.output_temp_files

    combine = Combine(output_file)
    combine.combine_files(temp_files_list)
    print('Done')
