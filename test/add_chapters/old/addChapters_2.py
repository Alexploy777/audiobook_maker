import os
import tempfile
import subprocess
from check_chapters_ffmpeg import extract_chapters_with_ffprobe, format_time

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class MergeAndChapters:
    def __init__(self, input_files_list, output_file):
        self.input_files_list = input_files_list
        self.output_file = output_file

    def merge(self):
        """Метод для объединения m4b файлов в один."""
        # Создаем корректный список файлов для ffmpeg, каждый на отдельной строке с префиксом 'file '
        try:
            with open('filelist.txt', 'w', encoding='utf-8') as f:
                for file in self.input_files_list:
                    f.write(f"file '{file}'\n")

            # Запускаем ffmpeg для объединения файлов
            merge_command = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt',
                '-c', 'copy', '-y', self.output_file
            ]
            result = subprocess.run(merge_command, capture_output=True, text=True, encoding='utf-8')

            # Проверка успешности выполнения команды
            if result.returncode != 0:
                print("Ошибка при объединении файлов:", result.stderr)
            else:
                print("Объединение файлов прошло успешно.")
        except subprocess.CalledProcessError as e:
            print(f'Ошибка при объединении файлов: {e}')
        finally:
            os.remove('filelist.txt')

    def add_chapters(self):
        durations = []
        for input_file in self.input_files_list:
            result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
                                     'default=noprint_wrappers=1:nokey=1', input_file],
                                    capture_output=True, text=True)
            durations.append(float(result.stdout.strip()))

        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as chapters_file:
            start_time = 0
            for i, duration in enumerate(durations, 1):
                chapters_file.write(f"CHAPTER{i:02d}={format_time(start_time)}\n")
                chapters_file.write(f"CHAPTER{i:02d}NAME=Chapter {i}\n")
                start_time += duration
            chapters_path = chapters_file.name

        try:
            subprocess.run(['ffmpeg', '-i', self.output_file, '-f', 'ffmetadata', '-i', chapters_path,
                            '-map_metadata', '1', '-codec', 'copy', '-y', self.output_file], check=True)
            print("Главы добавлены успешно.")
        except subprocess.CalledProcessError:
            print("Ошибка при добавлении глав.")
        finally:
            os.remove(chapters_path)

    def checkChapters(self):
        chapters = extract_chapters_with_ffprobe(self.output_file)
        if not chapters:
            print("Главы не найдены.")
            return
        for i, (title, start_time) in enumerate(chapters, 1):
            print(f"Глава {i}: {title} - старт с {format_time(start_time)} сек.")


if __name__ == '__main__':
    input_files_list = ['1.m4b', '2.m4b', '3.m4b']
    output_file = 'output.m4b'

    mergeandchapters = MergeAndChapters(input_files_list, output_file)
    mergeandchapters.merge()
    mergeandchapters.add_chapters()
    mergeandchapters.checkChapters()
