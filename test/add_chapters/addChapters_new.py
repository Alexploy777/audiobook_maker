import os
import shutil
import tempfile
import subprocess
import ffmpeg

from check_chapters_ffmpeg import extract_chapters_with_ffprobe, format_time

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class M4bMerger:
    def __init__(self, input_files_list, output_file):
        """
        Инициализация M4bMerger с путями к исходным файлам и результирующему файлу.
        """
        self.input_files_list = input_files_list
        self.output_file = output_file

    def analyze_durations(self):
        """
        Определяет длительность каждого исходного файла.
        """
        durations = []
        for file in self.input_files_list:
            probe = ffmpeg.probe(file)
            duration = float(probe['format']['duration'])
            durations.append(duration)
        return durations

    def merge_files(self, volume_adjustment=None):
        """
        Объединяет файлы. При необходимости применяет фильтр изменения громкости.
        """
        input_streams = [ffmpeg.input(file) for file in self.input_files_list]
        concat = ffmpeg.concat(*input_streams, v=0, a=1).node
        audio = concat[0]

        # Применение фильтра громкости
        if volume_adjustment:
            audio = audio.filter('volume', volume_adjustment)

        ffmpeg.output(audio, self.output_file).run(overwrite_output=True)

    def delete_source_files(self):
        """
        Опционально удаляет исходные файлы.
        """
        for file in self.input_files_list:
            os.remove(file)
            print(f"Удален файл: {file}")


class AddChapters:
    def __init__(self, merged_file, chapter_durations):
        """
        Инициализация AddChapters с путем к объединенному файлу и длительностями глав.
        """
        self.merged_file = merged_file
        self.chapter_durations = chapter_durations

    def create_metadata_file(self):
        """
        Создает временный файл с метаданными для глав.
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ffmetadata")
        start_time = 0
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            f.write(";FFMETADATA1\n")
            for i, duration in enumerate(self.chapter_durations):
                f.write(f"[CHAPTER]\nTIMEBASE=1/1000\n")
                f.write(f"START={int(start_time * 1000)}\n")
                f.write(f"END={int((start_time + duration) * 1000)}\n")
                f.write(f"title=chapter_{i + 1:03d}\n")
                start_time += duration
        return temp_file.name

    def add_chapters(self):
        """
        Добавляет главы в объединенный файл, используя временный файл метаданных.
        """
        metadata_file = self.create_metadata_file()
        output_with_chapters = self.merged_file.replace(".m4b", "_with_chapters.m4b")

        ffmpeg.input(self.merged_file).output(
            output_with_chapters,
            map_metadata=metadata_file,
            codec="copy"
        ).run(overwrite_output=True)

        os.remove(metadata_file)  # Удаляем временный файл с метаданными
        print(f"Файл с главами создан: {output_with_chapters}")


def checkChapters(file_for_analise):
    """Проверка наличия и отображение глав в файле."""
    chapters = extract_chapters_with_ffprobe(file_for_analise)
    if not chapters:
        print("Главы не найдены.")
        return
    for i, (title, start_time) in enumerate(chapters, 1):
        print(f"Глава {i}: {title} - старт с {format_time(start_time)} сек.")


if __name__ == '__main__':
    input_files = ['1.m4b', '2.m4b', '3.m4b']
    output_file = 'output.m4b'

    # Создаем объект для объединения файлов
    merger = M4bMerger(input_files, output_file)

    # Анализируем длительности
    durations = merger.analyze_durations()
    print(f"Длительности исходных файлов: {durations}")

    # Объединяем файлы с опциональным изменением громкости
    merger.merge_files(volume_adjustment="0.8")

    # Удаляем исходные файлы (опционально)
    # merger.delete_source_files()

    # Добавляем главы в объединенный файл
    chapter_adder = AddChapters(output_file, durations)
    chapter_adder.add_chapters()
