import sys
from PyQt5.QtCore import QRunnable, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from pydub import AudioSegment
import tempfile
import os


class ConverterSignals(QObject):
    progress_bar_signal = pyqtSignal(int)
    label_info_signal = pyqtSignal(str)
    all_tasks_completed = pyqtSignal()  # Сигнал о завершении всех заданий


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
        self.output_temp_files_list[self.index] = output_file
        self.my_signals.progress_bar_signal.emit(self.index)  # Отправляем сигнал о завершении задания
        self.my_signals.label_info_signal.emit(f'Файл {os.path.abspath(self.file)} успешно сконвертирован')

    def convert_mp3_to_m4b(self, input_path):
        try:
            audio = AudioSegment.from_mp3(input_path)
            output_buffer = tempfile.NamedTemporaryFile(suffix='.m4b', delete=False)  # Создаем временный файл
            audio.export(output_buffer.name, format="mp4", codec="aac", bitrate=self.bitrate)
            output_buffer.close()  # Явно закрываем временный файл
            print(f"Файл успешно конвертирован: {input_path}")
            return output_buffer

        except Exception as e:
            print(f"Ошибка при конвертации файла {input_path}: {e}")
            return None


if __name__ == '__main__':
    pass
