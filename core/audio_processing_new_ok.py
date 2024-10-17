import subprocess
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
    all_files_merged = pyqtSignal()  # Сигнал об окончании объединения


class M4BMerger(QRunnable):
    def __init__(self, input_files, output_file):
        super().__init__()
        self.input_files = input_files  # Список буферов аудиофайлов
        self.output_file = output_file  # Финальный выходной файл
        self.my_signals = ConverterSignals()

    def merge_files(self):
        """Объединяем m4b файлы с помощью ffmpeg, используя временный список файлов."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                for file_data in self.input_files:
                    if file_data:
                        # temp_file.write(f"file '{file_data.name}'\n")
                        temp_file.write(f"file '{file_data}'\n")
            print(temp_file.name)
            ffmpeg_command = [
                'ffmpeg',
                '-f', 'concat',  # формат ввода: список файлов
                '-safe', '0',  # разрешаем использовать небезопасные символы в путях
                '-i', temp_file.name,  # ввод через временный файл списка
                '-c', 'copy',  # копируем содержимое без перекодирования
                '-y',  # перезаписываем выходной файл без предупреждения
                self.output_file  # выходной файл
            ]

            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f'Файлы успешно объединены в {self.output_file}')
        except subprocess.CalledProcessError as e:
            print(f'Ошибка при объединении файлов: {e}')
        finally:
            os.remove(temp_file.name)  # Удаляем временный файл списка после завершения работы

    def run(self):
        """Основной метод для выполнения всех шагов."""
        self.merge_files()
        self.my_signals.all_files_merged.emit()


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
