import os
import subprocess

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


def create_ffmetadata_file(metadata_file):
    # Формируем строки метаданных для глав
    metadata_content = """;FFMETADATA1
[CHAPTER]
TIMEBASE=1/1000
START=0
END=395490
title=Chapter 1
[CHAPTER]
TIMEBASE=1/1000
START=395490
END=1171620
title=Chapter 2
[CHAPTER]
TIMEBASE=1/1000
START=1171620
END=1940820
title=Chapter 3
"""

    # Сохраняем метаданные в файл
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write(metadata_content)


def add_chapters_with_ffmpeg(audio_file, metadata_file, output_file):
    try:
        # Запуск команды ffmpeg с метаданными и главами
        result = subprocess.run([
            'ffmpeg', '-i', audio_file, '-i', metadata_file,
            '-map_metadata', '1', '-map_chapters', '1',  # Привязка метаданных и глав
            '-c', 'copy',  # Копирование кодека без перекодирования
            '-f', 'ipod', output_file,  # Формат файла как iPod (m4b)
            '-y'  # Перезапись, если файл уже существует
        ], check=True, text=True, capture_output=True)

        print("Файл успешно создан с главами.")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("Произошла ошибка при добавлении глав.")
        print(e.stderr)


# Путь к аудиофайлу и файлу метаданных
audio_file = 'output.m4b'
metadata_file = 'chapters.ffmetadata'
output_file = 'final_output_with_chapters.m4b'

# Создаем файл метаданных
create_ffmetadata_file(metadata_file)

# Вызов функции для добавления глав
add_chapters_with_ffmpeg(audio_file, metadata_file, output_file)
