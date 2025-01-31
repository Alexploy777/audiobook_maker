from .convertersignals import ConverterSignals
from PyQt5.QtCore import QRunnable, pyqtSlot
from data import Config
import os
import subprocess
import tempfile


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
                # print(f"Файл не найден: {input_path}")
                self.my_signals.label_info_signal.emit(f"Файл не найден: {input_path}")
                return None

            # Создаём временный файл
            output_buffer = tempfile.NamedTemporaryFile(suffix=self.output_format, delete=False)
            output_buffer.close()  # Закрываем, чтобы FFmpeg мог записать в него

            # Команда для FFmpeg ffmpeg -i input.mp3 -vn -c:a aac output.m4b
            # print(self.bitrate)
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
                # print(f"Ошибка FFmpeg: {process.stderr}")
                self.my_signals.label_info_signal.emit(f"Файл не найден: {input_path}")
                return None

            # print(f"Файл успешно конвертирован: {input_path}")
            self.my_signals.label_info_signal.emit(f"Файл успешно конвертирован: {input_path}")
            return output_buffer

        except Exception as e:
            # print(f"Ошибка при конвертации файла {input_path}: {e}")
            self.my_signals.label_info_signal.emit(f"Ошибка при конвертации файла {input_path}: {e}")
            return None
