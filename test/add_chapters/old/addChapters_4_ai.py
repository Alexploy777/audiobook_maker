import os
import shutil
import tempfile
import subprocess
from check_chapters_ffmpeg import extract_chapters_with_ffprobe, format_time

os.environ['PATH'] += os.pathsep + os.path.abspath('external')

import subprocess
import os


def add_chapters_with_ffmpeg(audio_file, metadata_file, output_file):
    try:
        # Запускаем команду ffmpeg для конвертации с добавлением метаданных глав
        result = subprocess.run([
            'ffmpeg', '-i', audio_file, '-i', metadata_file,
            '-map_metadata', '1', '-map_chapters', '1',  # Привязка метаданных и глав
            '-c', 'copy',  # Копирование кодека без перекодирования
            '-f', 'ipod', output_file,  # Формат файла как iPod (m4b)
            '-y'  # Перезапись, если файл уже существует
        ], check=True, text=True, capture_output=True)

        # Если команда выполнена успешно, выводим сообщение
        print("Файл успешно создан с главами.")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        # Обработка ошибок в случае неудачи
        print("Произошла ошибка при добавлении глав.")
        print(e.stderr)


# Путь к аудиофайлу и файлу метаданных
audio_file = 'output.m4b'
metadata_file = 'chapters.txt'
output_file = 'final_output_with_chapters.m4b'

# Вызов функции
add_chapters_with_ffmpeg(audio_file, metadata_file, output_file)
