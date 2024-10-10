import os
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot, QObject, pyqtSignal
from pydub import AudioSegment

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class ConverterSignals(QObject):
    finished = pyqtSignal()  # Сигнал, когда задача завершена


class Converter(QRunnable):
    def __init__(self, file, output_temp_file, output_temp_files_list, index):
        super().__init__()
        self.input_path = file
        self.output_temp_file = output_temp_file
        self.output_temp_files_list = output_temp_files_list
        self.index = index
        self.signals = ConverterSignals()

    @pyqtSlot()
    def run(self):
        output_file = self.convert_mp3_to_m4b(self.input_path, self.output_temp_file)
        self.output_temp_files_list[self.index] = output_file  # Запись результата по индексу
        self.signals.finished.emit()  # Отправляем сигнал о завершении

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
    all_tasks_finished = pyqtSignal()  # Сигнал, когда все задачи завершены

    def __init__(self, output_dir_name):
        super().__init__()
        self.output_dir_name = output_dir_name
        self.thread_pool = QThreadPool()
        self.output_temp_files_list = []  # Список для хранения путей к выходным файлам
        self.finished_count = 0
        self.total_tasks = 0

    def get_output_file_path(self, input_path):
        temp = os.path.abspath(input_path)
        dir_name = os.path.dirname(os.path.dirname(temp))
        full_output_dir = os.path.join(dir_name, self.output_dir_name)
        os.makedirs(full_output_dir, exist_ok=True)
        name = os.path.basename(temp).split(os.extsep)[0]
        output_name = os.path.join(str(full_output_dir), name + '.m4b')
        return output_name

    def start(self, input_list):
        self.output_temp_files_list = [None] * len(input_list)  # Инициализируем список с None для каждого файла
        self.total_tasks = len(input_list)
        self.finished_count = 0

        for index, file in enumerate(input_list):
            output_temp_file = self.get_output_file_path(file)
            converter = Converter(file, output_temp_file, self.output_temp_files_list, index)
            converter.signals.finished.connect(self.on_task_finished)  # Подключаем сигнал
            self.thread_pool.start(converter)

        # # Ждём завершения всех потоков
        # self.thread_pool.waitForDone()

    def on_task_finished(self):
        self.finished_count += 1
        if self.finished_count == self.total_tasks:
            print("Все задачи завершены!")
            self.all_tasks_finished.emit()  # Отправляем сигнал о завершении всех задач


class Combine:
    def __init__(self, output_file):
        self.output_file = output_file

    def combine_files(self, temp_files_list):
        combined = AudioSegment.empty()
        try:
            for index, file_path in enumerate(temp_files_list):
                audio = AudioSegment.from_file(file_path, format="mp4")
                combined += audio
            combined.export(self.output_file, format="mp4", codec="aac")
        finally:
            for temp_file in temp_files_list:
                if os.path.exists(temp_file):
                    os.remove(temp_file)


if __name__ == '__main__':
    input_list = ['mp3/1.mp3', 'mp3/2.mp3', 'mp3/3.mp3', 'mp3/4.mp3']
    output_dir_name = 'temp'
    output_file = 'final.m4b'

    converter_manager = ConverterManager(output_dir_name)

    def on_all_tasks_done():
        print('Конвертация завершена, начинается объединение файлов...')
        combine = Combine(output_file)
        combine.combine_files(converter_manager.output_temp_files_list)
        print('Объединение завершено. Done')

    # Подключаем завершение всех задач к функции объединения файлов
    converter_manager.all_tasks_finished.connect(on_all_tasks_done)

    # Стартуем конвертацию
    converter_manager.start(input_list)
