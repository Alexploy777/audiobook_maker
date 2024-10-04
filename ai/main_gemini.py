import os


# Добавляем пути к ffmpeg и ffprobe в переменную окружения PATH
# ffmpeg_path = os.path.join(os.path.dirname(__file__), "external", "ffmpeg.exe")
# ffprobe_path = os.path.join(os.path.dirname(__file__), "external", "ffprobe.exe")
# os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
#
# # Устанавливаем переменные окружения для Pydub
# os.environ["FFMPEG_BINARY"] = ffmpeg_path
# os.environ["FFPROBE_BINARY"] = ffprobe_path
#
# # Определяем пути к входному и выходному файлам
# input_file = "files/1.mp3"
# output_file = "files/1.m4b"
#
# # Загружаем аудиофайл
# sound = pydub.AudioSegment.from_mp3(input_file)
#
# # Экспортируем в формат m4b
# sound.export(output_file, format="mp4", codec="aac")
#
# print("Конвертация завершена успешно.")

def add_file_to_system_path(external_dir_name):
    # Абсолютный путь к директории с файлами
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_external_dir_name = os.path.join(base_dir, external_dir_name)

    # Добавляем пути в переменную окружения PATH
    os.environ["PATH"] += os.pathsep + full_external_dir_name


    # Пути к ffmpeg и ffprobe
    ffmpeg_exec = os.path.join(base_dir, external_dir_name, 'ffmpeg.exe')
    ffprobe_exec = os.path.join(base_dir, external_dir_name, 'ffprobe.exe')


    # Устанавливаем переменные окружения для Pydub
    os.environ["FFMPEG_BINARY"] = ffmpeg_exec
    os.environ["FFPROBE_BINARY"] = ffprobe_exec

    # pydub.AudioSegment.converter = ffmpeg_exec
    # pydub.AudioSegment.ffprobe = ffprobe_exec

add_file_to_system_path("external")

import pydub