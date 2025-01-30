# # core/addchapters.py
# import os
# import shutil
# import subprocess
# import tempfile
#
#
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


import subprocess
import tempfile
import os
import shutil
import re

class AddChapters:
    def __init__(self, output_file, chapter_durations, my_signals=None):
        self.output_file = output_file
        self.chapter_durations = chapter_durations
        self.my_signals = my_signals  # Функция для обновления прогресса
        self.my_signals.progress_bar_signal.emit(0)
        self.my_signals.label_info_signal.emit('Добавляю главы..')

    def create_chapters_metadata(self):
        metadata_content = ";FFMETADATA1\n"
        current_time = 0
        for i, duration in enumerate(self.chapter_durations):
            start_time = current_time
            end_time = current_time + duration
            metadata_content += f"[CHAPTER]\nTIMEBASE=1/1\nSTART={int(start_time)}\nEND={int(end_time)}\ntitle=chapter_{i + 1:03}\n"
            current_time = end_time
        return metadata_content

    def add_chapters(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ffmetadata") as f:
            f.write(self.create_chapters_metadata().encode('utf-8'))
        metadata_file = f.name
        output_temp_file = tempfile.mktemp(suffix=".m4b")

        try:
            # Команда ffmpeg для добавления глав
            ffmpeg_command = [
                "ffmpeg", "-i", self.output_file, "-i", metadata_file,
                "-map_metadata", "1", "-codec", "copy", output_temp_file
            ]

            # Запуск ffmpeg с отслеживанием прогресса
            process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

            total_duration = sum(self.chapter_durations)
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
                        if self.my_signals:
                            self.my_signals.progress_bar_signal.emit(progress)  # Обновляем прогресс

            process.wait()
            if process.returncode == 0:
                # print(f'Главы успешно добавлены в {self.output_file}')
                self.my_signals.label_info_signal.emit(f'Главы успешно добавлены в {self.output_file}')
            else:
                # print(f'Ошибка при добавлении глав: {process.stderr.read()}')
                self.my_signals.label_info_signal.emit(f'Ошибка при добавлении глав: {process.stderr.read()}')

            # Заменяем оригинальный файл временным
            shutil.move(output_temp_file, self.output_file)
        except Exception as e:
            # print(f'Ошибка при добавлении глав: {e}')
            self.my_signals.label_info_signal.emit(f'Ошибка при добавлении глав: {e}')
        finally:
            os.remove(metadata_file)
            if os.path.exists(output_temp_file):
                os.remove(output_temp_file)