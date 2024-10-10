import os
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot
from pydub import AudioSegment
# from PyQt5.QtCore import QFutureWatcher

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


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


class ConverterManager:
    def __init__(self, output_dir_name):
        self.output_dir_name = output_dir_name
        self.thread_pool = QThreadPool()
        self.output_temp_files_list = []  # Список для хранения путей к выходным файлам
        # self.watcher = QFutureWatcher()

    def get_output_file_path(self, input_path):
        '''
        Функция формирует и возвращает абсолютный путь временного файла с исходным именем
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

    def start(self, input_list):
        self.output_temp_files_list = [None] * len(input_list)  # Инициализируем список с None для каждого файла
        futures = []
        for index, file in enumerate(input_list):
            output_temp_file = self.get_output_file_path(file)
            converter = Converter(file, output_temp_file, self.output_temp_files_list, index)
            # self.thread_pool.start(converter)
            future = self.thread_pool.start(converter)
            futures.append(future)

        # Ждём завершения всех потоков
        self.thread_pool.waitForDone()

        # self.watcher.setFuture(futures[-1])  # Отслеживаем последний future
        # self.watcher.finished.connect(self.on_conversion_done)

    def on_conversion_done(self):
        print("Конвертация всех файлов завершена!")


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
    temp_files_list = converter_manager.output_temp_files_list

    combine = Combine(output_file)
    combine.combine_files(temp_files_list)
    print('Done')
