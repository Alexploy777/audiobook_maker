import os
import re
import subprocess
import sys
import tempfile
import types

from PyQt5.QtCore import QRunnable, pyqtSignal, QObject, pyqtSlot
from mutagen.mp4 import MP4Cover, MP4
from pydub import AudioSegment

os.environ['FFMPEG_LOG_LEVEL'] = 'quiet'


class ConverterSignals(QObject):
    progress_bar_signal = pyqtSignal(int)
    label_info_signal = pyqtSignal(str)
    label_info_signal_2 = pyqtSignal(str)
    all_tasks_completed = pyqtSignal()  # Сигнал о завершении всех заданий
    all_files_merged = pyqtSignal()  # Сигнал об окончании объединения


class M4BMerger(QRunnable):
    def __init__(self, input_files, output_file, metadata):
        super().__init__()
        self.input_files = input_files  # Список буферов аудиофайлов
        self.output_file = output_file  # Финальный выходной файл
        self.metadata = metadata
        self.my_signals = ConverterSignals()

    def merge_files(self):
        """Объединяем m4b файлы с помощью ffmpeg, используя временный список файлов и добавляем главы."""
        self.my_signals.label_info_signal.emit('Начинаю объединять файлы')
        self.my_signals.progress_bar_signal.emit(30)
        try:
            # Шаг 1: Создаем временный файл для списка файлов
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                for file_data in self.input_files:
                    if file_data:
                        temp_file.write(f"file '{file_data}'\n")

            # Шаг 2: Создаем временный файл для метаданных глав
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as chapters_file:
                start_time = 0.0  # Время начала каждой главы
                for index, file_data in enumerate(self.input_files):
                    if file_data:
                        # Получаем продолжительность каждого файла
                        duration_command = [
                            'ffprobe',
                            '-v', 'error',
                            '-show_entries', 'format=duration',
                            '-of', 'default=noprint_wrappers=1:nokey=1',
                            file_data
                        ]
                        result = subprocess.run(duration_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        duration = float(result.stdout.strip())

                        # Пишем главу в метаданные
                        chapters_file.write(f"[CHAPTER]\n")
                        chapters_file.write(f"TIMEBASE=1/1\n")
                        chapters_file.write(f"START={int(start_time)}\n")
                        chapters_file.write(f"END={int(start_time + duration)}\n")
                        chapters_file.write(f"title=Chapter {index + 1}\n")

                        start_time += duration  # Обновляем время начала следующей главы

            # Шаг 3: Объединяем файлы и добавляем главы через метаданные
            ffmpeg_command = [
                'ffmpeg',
                '-f', 'concat',  # формат ввода: список файлов
                '-safe', '0',  # разрешаем использовать небезопасные символы в путях
                '-i', temp_file.name,  # ввод через временный файл списка
                '-i', chapters_file.name,  # ввод метаданных глав
                '-map_metadata', '1',  # используем метаданные из второго файла (главы)
                '-c', 'copy',  # копируем содержимое без перекодирования
                '-y',  # перезаписываем выходной файл без предупреждения
                self.output_file  # выходной файл
            ]

            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f'Файлы успешно объединены в {self.output_file} с добавлением глав')

        except subprocess.CalledProcessError as e:
            print(f'Ошибка при объединении файлов: {e}')
        finally:
            # Удаляем временные файлы после завершения работы
            os.remove(temp_file.name)
            os.remove(chapters_file.name)
            self.my_signals.label_info_signal.emit('Файлы объединены')

    # def merge_files(self):
    #     """Объединяем m4b файлы с помощью ffmpeg, используя временный список файлов."""
    #     self.my_signals.label_info_signal.emit('Начинаю объединять файлы')
    #     self.my_signals.progress_bar_signal.emit(30)
    #     try:
    #         with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
    #             for file_data in self.input_files:
    #                 if file_data:
    #                     # temp_file.write(f"file '{file_data.name}'\n")
    #                     temp_file.write(f"file '{file_data}'\n")
    #         print(temp_file.name)
    #         ffmpeg_command = [
    #             'ffmpeg',
    #             '-f', 'concat',  # формат ввода: список файлов
    #             '-safe', '0',  # разрешаем использовать небезопасные символы в путях
    #             '-i', temp_file.name,  # ввод через временный файл списка
    #             '-c', 'copy',  # копируем содержимое без перекодирования
    #             '-y',  # перезаписываем выходной файл без предупреждения
    #             self.output_file  # выходной файл
    #         ]
    #
    #         subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #         print(f'Файлы успешно объединены в {self.output_file}')
    #     except subprocess.CalledProcessError as e:
    #         print(f'Ошибка при объединении файлов: {e}')
    #     finally:
    #         os.remove(temp_file.name)  # Удаляем временный файл списка после завершения работы

    def add_cover_and_metadata(self, output_path, metadata):
        self.my_signals.label_info_signal.emit('Добавляю метаданные')
        self.my_signals.progress_bar_signal.emit(60)
        audio = MP4(output_path)

        # Добавление метаданных
        audio['\xa9nam'] = metadata.get("title")
        audio['\xa9ART'] = metadata.get("artist")
        audio['\xa9alb'] = metadata.get("album")
        audio['\xa9day'] = metadata.get("year")
        audio['\xa9gen'] = metadata.get("genre")

        if cover_image_bytes := metadata.get('image_data'):
            cover = MP4Cover(cover_image_bytes, imageformat=MP4Cover.FORMAT_JPEG)
            audio['covr'] = [cover]
        self.my_signals.progress_bar_signal.emit(90)
        self.my_signals.label_info_signal.emit('Сохраняю файл')
        audio.save()

    def run(self):
        """Основной метод для выполнения всех шагов."""
        self.merge_files()
        self.add_cover_and_metadata(self.output_file, self.metadata)
        self.my_signals.all_files_merged.emit()


from PyQt5.QtCore import QRunnable, pyqtSlot
import subprocess
import os
import tempfile

from PyQt5.QtCore import QRunnable, pyqtSlot
import subprocess
import os
import tempfile


class Converter(QRunnable):
    def __init__(self, index, quantity, file, output_temp_files_list, bitrate):
        super().__init__()
        self.index = index
        self.quantity = quantity
        self.my_signals = ConverterSignals()
        self.file = file
        self.output_temp_files_list = output_temp_files_list
        self.bitrate = bitrate

    @pyqtSlot()
    def run(self):
        """Запускает выполнение задания."""
        output_file = self.convert_mp3_to_m4b(self.file)
        if output_file:
            self.output_temp_files_list[self.index] = output_file
            self.my_signals.progress_bar_signal.emit(self.index)  # Отправляем сигнал о завершении задания
            self.my_signals.label_info_signal.emit(f'Сконвертирован файл:')
            self.my_signals.label_info_signal_2.emit(f'{os.path.abspath(self.file)}')

    def convert_mp3_to_m4b(self, input_path):
        try:
            # Создаем временный файл для m4b
            output_buffer = tempfile.NamedTemporaryFile(suffix='.m4b', delete=False)

            # Команда для вызова ffmpeg через subprocess
            ffmpeg_command = [
                'ffmpeg', '-i', input_path, '-c:a', 'aac', '-b:a', self.bitrate, output_buffer.name
            ]

            # Лог для отслеживания команды
            print(f"Запуск команды: {' '.join(ffmpeg_command)}")

            # Используем Popen для асинхронного запуска процесса
            process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW)

            # Ожидание завершения процесса
            stdout, stderr = process.communicate()

            # Лог выводов процесса
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")

            if process.returncode == 0:
                print(f"Файл успешно конвертирован: {input_path}")
                return output_buffer.name  # Возвращаем путь к времянке
            else:
                print(f"Ошибка при конвертации файла: {stderr.decode()}")
                return None

        except Exception as e:
            print(f"Ошибка при конвертации файла {input_path}: {e}")
            return None


# class Converter(QRunnable):
#     def __init__(self, index, quantity, file, output_temp_files_list, bitrate):
#         super().__init__()
#         self.index = index
#         self.quantity = quantity
#         self.my_signals = ConverterSignals()
#         self.file = file
#         self.output_temp_files_list = output_temp_files_list
#         self.bitrate = bitrate
#
#     @pyqtSlot()
#     def run(self):
#         """Запускает выполнение задания."""
#         output_file = self.convert_mp3_to_m4b(self.file)
#
#         self.output_temp_files_list[self.index] = output_file
#         self.my_signals.progress_bar_signal.emit(self.index)  # Отправляем сигнал о завершении задания
#         self.my_signals.label_info_signal.emit(f'сконвертирован файл:')
#         self.my_signals.label_info_signal_2.emit(f'{os.path.abspath(self.file)}')
#
#     def convert_mp3_to_m4b(self, input_path):
#         try:
#             os.environ['FFMPEG_LOG_LEVEL'] = 'quiet'
#             audio = AudioSegment.from_mp3(input_path)
#             output_buffer = tempfile.NamedTemporaryFile(suffix='.m4b', delete=False)  # Создаем временный файл
#
#             audio.export(output_buffer.name, format="mp4", codec="aac", bitrate=self.bitrate)
#             output_buffer.close()  # Явно закрываем временный файл
#             print(f"Файл успешно конвертирован: {input_path}")
#             return output_buffer
#
#         except Exception as e:
#             print(f"Ошибка при конвертации файла {input_path}: {e}")
#             return None


if __name__ == '__main__':
    pass
