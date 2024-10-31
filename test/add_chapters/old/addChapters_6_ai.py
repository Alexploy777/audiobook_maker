import os
import subprocess

os.environ['PATH'] += os.pathsep + os.path.abspath('external')

import subprocess


def add_chapters_with_ffmpeg(audio_file, metadata_file, output_file):
    try:
        result = subprocess.run([
            'ffmpeg', '-i', audio_file, '-i', metadata_file,
            '-map_metadata', '1', '-map_chapters', '1',
            '-c', 'copy',
            '-f', 'ipod', output_file,
            '-y'
        ], check=True, text=True, capture_output=True)

        print("Файл успешно создан с главами.")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("Произошла ошибка при добавлении глав.")
        print(e.stderr)


# Путь к файлам
audio_file = 'output.m4b'
metadata_file = 'chapters.ffmetadata'
output_file = 'final_output_with_chapters.m4b'

# Запуск команды для добавления глав
add_chapters_with_ffmpeg(audio_file, metadata_file, output_file)
