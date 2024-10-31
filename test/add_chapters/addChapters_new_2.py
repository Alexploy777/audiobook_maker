import os
import subprocess
import tempfile

from check_chapters_ffmpeg import extract_chapters_with_ffprobe, format_time

# Подключение ffmpeg из директории 'external'
os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class M4bMerger:
    def __init__(self, input_files_list, output_file):
        # self.input_files_list = input_files_list
        # self.output_file = output_file
        # Преобразование путей к абсолютным для исключения ошибок поиска файлов
        self.input_files_list = [os.path.abspath(file) for file in input_files_list]
        self.output_file = os.path.abspath(output_file)

    def get_durations(self):
        durations = []
        for file in self.input_files_list:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                 "default=noprint_wrappers=1:nokey=1", file],
                capture_output=True, text=True
            )
            duration = float(result.stdout.strip())
            durations.append(duration)
        return durations

    def merge_files(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            for file in self.input_files_list:
                f.write(f"file '{file}'\n".encode('utf-8'))
        merge_list_file = f.name
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", merge_list_file, "-c", "copy", '-y', self.output_file
        ])
        os.remove(merge_list_file)


class AddChapters:
    def __init__(self, output_file, chapter_durations):
        self.output_file = output_file
        self.chapter_durations = chapter_durations

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
        # output_with_chapters = self.output_file.replace(".m4b", "_with_chapters.m4b")
        subprocess.run([
            "ffmpeg", "-i", self.output_file, "-i", metadata_file, "-map_metadata", "1", "-codec", "copy", '-y',
            self.output_file
        ])
        os.remove(metadata_file)


def checkChapters(file_for_analise):
    """Проверка наличия и отображение глав в файле."""
    chapters = extract_chapters_with_ffprobe(file_for_analise)
    if not chapters:
        print("Главы не найдены.")
        return
    for i, (title, start_time) in enumerate(chapters, 1):
        print(f"Глава {i}: {title} - старт с {format_time(start_time)} сек.")


if __name__ == '__main__':
    # Пример использования
    input_files_list = ['1.m4b', '2.m4b', '3.m4b']
    output_file = 'output.m4b'

    # Шаг 1: Объединение файлов
    merger = M4bMerger(input_files_list, output_file)
    merger.merge_files()

    # Шаг 2: Добавление глав
    durations = merger.get_durations()
    chapter_adder = AddChapters(output_file, durations)
    chapter_adder.add_chapters()

    # Проверка наличия глав
    checkChapters('output_with_chapters.m4b')
