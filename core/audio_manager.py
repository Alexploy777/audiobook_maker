import os
import shutil
import subprocess
import tempfile

from PyQt5.QtCore import QRunnable, pyqtSignal, QObject, pyqtSlot
from mutagen.mp4 import MP4Cover, MP4

from .convertersignals import ConverterSignals
from .addchapters import AddChapters
from .addcoverandmetadata import AddCoverAndMetadata
from data import Config


## creationflags=subprocess.CREATE_NO_WINDOW - подавляем консольные окна

# class ConverterSignals(QObject):
#     progress_bar_signal = pyqtSignal(int)
#     label_info_signal = pyqtSignal(str)
#     label_info_signal_2 = pyqtSignal(str)
#     all_tasks_completed = pyqtSignal()  # Сигнал о завершении всех заданий
#     all_tasks_complete = pyqtSignal()  # Сигнал об окончании объединения


class M4bMerger(QRunnable):  # Потом убрать!
    # class M4bMerger:
    def __init__(self, input_files, output_file, metadata):
        super().__init__()
        self.input_files = input_files  # Список путей к аудиофайлам
        self.output_file = output_file  # Финальный выходной файл
        self.metadata = metadata
        self.my_signals = ConverterSignals()
        self.durations = self.get_durations()

    def get_durations(self):
        durations = []
        for file in self.input_files:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                 "default=noprint_wrappers=1:nokey=1", file],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            duration = float(result.stdout.strip())
            durations.append(duration)
        return durations

    def merge_files(self):
        """Объединение m4b файлов с помощью ffmpeg через временный список файлов."""
        self.my_signals.label_info_signal.emit('Начинаю объединять файлы')
        self.my_signals.progress_bar_signal.emit(30)
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                for file_data in self.input_files:
                    if file_data:
                        temp_file.write(f"file '{file_data}'\n")
            print(temp_file.name)

            ffmpeg_command = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', temp_file.name,
                '-c', 'copy',
                '-y',
                self.output_file
            ]
            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            print(f'Файлы успешно объединены в {self.output_file}')
        except subprocess.CalledProcessError as e:
            print(f'Ошибка при объединении файлов: {e}')
        finally:
            os.remove(temp_file.name)

    def run(self):
        """Основной метод для выполнения всех шагов."""
        self.merge_files()
        # self.add_chapters()

        chapter_adder = AddChapters(self.output_file, self.durations)
        chapter_adder.add_chapters()

        addcoverandmetadata = AddCoverAndMetadata(self.output_file, self.metadata)
        addcoverandmetadata.add_cover_and_metadata()

        self.my_signals.all_tasks_complete.emit()


# class AddCoverAndMetadata:
#     def __init__(self, output_file, metadata):
#         self.my_signals = ConverterSignals()
#         self.output_file = output_file
#         self.metadata = metadata
#
#     def add_cover_and_metadata(self):
#         self.my_signals.label_info_signal.emit('Добавляю метаданные')
#         self.my_signals.progress_bar_signal.emit(60)
#         audio = MP4(self.output_file)
#
#         # Добавление метаданных
#         audio['\xa9nam'] = self.metadata.get("title")
#         audio['\xa9ART'] = self.metadata.get("artist")
#         audio['\xa9alb'] = self.metadata.get("album")
#         audio['\xa9day'] = self.metadata.get("year")
#         audio['\xa9gen'] = self.metadata.get("genre")
#
#         if cover_image_bytes := self.metadata.get('image_data'):
#             cover = MP4Cover(cover_image_bytes, imageformat=MP4Cover.FORMAT_JPEG)
#             audio['covr'] = [cover]
#         self.my_signals.progress_bar_signal.emit(90)
#         self.my_signals.label_info_signal.emit('Сохраняю файл')
#         audio.save()


# class AddChapters:
#     def __init__(self, output_file, chapter_durations):
#         self.output_file = output_file
#         self.chapter_durations = chapter_durations
#
#     def create_chapters_metadata(self):
#         metadata_content = ";FFMETADATA1\n"
#         current_time = 0
#         for i, duration in enumerate(self.chapter_durations):
#             start_time = current_time
#             end_time = current_time + duration
#             metadata_content += f"[CHAPTER]\nTIMEBASE=1/1\nSTART={int(start_time)}\nEND={int(end_time)}\ntitle=chapter_{i + 1:03}\n"
#             current_time = end_time
#         return metadata_content
#
#     def add_chapters(self):
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".ffmetadata") as f:
#             f.write(self.create_chapters_metadata().encode('utf-8'))
#         metadata_file = f.name
#         output_temp_file = tempfile.mktemp(suffix=".m4b")
#
#         try:
#             # Создаем временный файл с главами
#             subprocess.run([
#                 "ffmpeg", "-i", self.output_file, "-i", metadata_file, "-map_metadata", "1", "-codec", "copy",
#                 output_temp_file
#             ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
#                 creationflags=subprocess.CREATE_NO_WINDOW)
#
#             # Заменяем оригинальный файл временным
#             shutil.move(output_temp_file, self.output_file)
#         finally:
#             os.remove(metadata_file)
#             if os.path.exists(output_temp_file):
#                 os.remove(output_temp_file)


class Converter(QRunnable):
    # class Converter:
    def __init__(self, index, quantity, file, output_temp_files_list, bitrate):
        super().__init__()
        self.index = index
        self.quantity = quantity
        self.my_signals = ConverterSignals()
        self.file = file
        self.output_temp_files_list = output_temp_files_list
        self.bitrate = bitrate

        self.audio_codec = Config.AUDIO_CODEC
        self.output_format = '.' + Config.OUTPUT_FORMAT

    @pyqtSlot()
    def run(self):
        """Запускает выполнение задания."""
        output_file = self.convert_mp3_to_m4b(self.file)

        self.output_temp_files_list[self.index] = output_file
        self.my_signals.progress_bar_signal.emit(self.index)  # Отправляем сигнал о завершении задания
        self.my_signals.label_info_signal.emit(f'сконвертирован файл:')
        self.my_signals.label_info_signal_2.emit(f'{os.path.abspath(self.file)}')

    def convert_mp3_to_m4b(self, input_path):
        try:
            # Проверка, существует ли файл
            if not os.path.isfile(input_path):
                print(f"Файл не найден: {input_path}")
                return None

            # Создаём временный файл
            output_buffer = tempfile.NamedTemporaryFile(suffix=self.output_format, delete=False)
            output_buffer.close()  # Закрываем, чтобы FFmpeg мог записать в него

            # Команда для FFmpeg ffmpeg -i input.mp3 -vn -c:a aac output.m4b
            print(self.bitrate)
            command = [
                'ffmpeg', '-i', input_path, '-vn', '-c:a', self.audio_codec, '-b:a', self.bitrate, '-y',
                # -y: перезаписываем файл, если существует
                output_buffer.name
            ]
            # Запускаем FFmpeg и выводим ошибки при необходимости
            process = subprocess.run(
                command,
                creationflags=subprocess.CREATE_NO_WINDOW,
                capture_output=True,
                text=True,
                encoding='utf-8',  # Добавляем utf-8 кодировку для безопасного чтения
                errors='ignore'  # Игнорируем недопустимые символы, чтобы избежать UnicodeDecodeError
            )

            if process.returncode != 0:  # Проверяем успешность выполнения
                print(f"Ошибка FFmpeg: {process.stderr}")
                return None

            print(f"Файл успешно конвертирован: {input_path}")
            return output_buffer

        except Exception as e:
            print(f"Ошибка при конвертации файла {input_path}: {e}")
            return None


if __name__ == '__main__':
    pass
