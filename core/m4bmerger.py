import os
import re
import subprocess
import tempfile

from PyQt5.QtCore import QRunnable

from .convertersignals import ConverterSignals
from .addchapters import AddChapters
from .addcoverandmetadata import AddCoverAndMetadata


class M4bMerger(QRunnable):
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
        self.my_signals.label_info_signal.emit('Начинаю объединять файлы..')
        self.my_signals.label_info_signal_2.emit('--><--')
        # self.my_signals.progress_bar_signal.emit(0)
        self.my_signals.progress_bar_signal_m4bmerger.emit(0)

        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                for file_data in self.input_files:
                    if file_data:
                        temp_file.write(f"file '{file_data}'\n")
            # print(temp_file.name)

            ffmpeg_command = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', temp_file.name,
                '-c', 'copy',
                '-y',
                self.output_file
            ]

            process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True, encoding='utf-8',
                                       creationflags=subprocess.CREATE_NO_WINDOW)

            total_duration = sum(self.durations)
            progress_pattern = re.compile(r'time=(\d{2}):(\d{2}):(\d{2})\.\d{2}')

            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    match = progress_pattern.search(output)
                    if match:
                        hours, minutes, seconds = map(int, match.groups())
                        current_time = hours * 3600 + minutes * 60 + seconds
                        progress = int((current_time / total_duration) * 100)
                        self.my_signals.progress_bar_signal_m4bmerger.emit(progress)

            process.wait()
            if process.returncode == 0:
                # print(f'Файлы успешно объединены в {self.output_file}')
                self.my_signals.label_info_signal.emit(f'Файлы успешно объединены в {self.output_file}')
            else:
                # print(f'Ошибка при объединении файлов: {process.stderr.read()}')
                self.my_signals.label_info_signal.emit(f'Ошибка при объединении файлов: {process.stderr.read()}')
        except Exception as e:
            # print(f'Ошибка при объединении файлов: {e}')
            self.my_signals.label_info_signal.emit(f'Ошибка при объединении файлов: {e}')
        finally:
            os.remove(temp_file.name)

    def run(self):
        """Основной метод для выполнения всех шагов."""
        self.merge_files()

        chapter_adder = AddChapters(self.output_file, self.durations, self.my_signals)
        chapter_adder.add_chapters()

        addcoverandmetadata = AddCoverAndMetadata(self.output_file, self.metadata, self.my_signals)
        addcoverandmetadata.add_cover_and_metadata()

        self.my_signals.signal_complete_merge.emit()


if __name__ == '__main__':
    pass
