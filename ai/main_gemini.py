import os
import pydub

# Добавляем пути к ffmpeg и ffprobe в переменную окружения PATH
ffmpeg_path = os.path.join(os.path.dirname(__file__), "external", "ffmpeg.exe")
ffprobe_path = os.path.join(os.path.dirname(__file__), "external", "ffprobe.exe")
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

# Устанавливаем переменные окружения для Pydub
os.environ["FFMPEG_BINARY"] = ffmpeg_path
os.environ["FFPROBE_BINARY"] = ffprobe_path

# Определяем пути к входному и выходному файлам
input_file = "files/1.mp3"
output_file = "files/1.m4b"

# Загружаем аудиофайл
sound = pydub.AudioSegment.from_mp3(input_file)

# Экспортируем в формат m4b
sound.export(output_file, format="mp4", codec="aac")

print("Конвертация завершена успешно.")