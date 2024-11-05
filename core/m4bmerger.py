import os
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

        chapter_adder = AddChapters(self.output_file, self.durations)
        chapter_adder.add_chapters()

        addcoverandmetadata = AddCoverAndMetadata(self.output_file, self.metadata)
        addcoverandmetadata.add_cover_and_metadata()

        self.my_signals.all_tasks_complete.emit()


if __name__ == '__main__':
    pass
