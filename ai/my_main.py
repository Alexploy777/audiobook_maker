import os
import subprocess

# Установка путей к ffmpeg и ffprobe через переменные окружения
os.environ["PATH"] += os.pathsep + os.path.join(os.path.dirname(__file__), "external")
os.environ["FFMPEG_BINARY"] = os.path.join(os.path.dirname(__file__), "external", "ffmpeg.exe")
os.environ["FFPROBE_BINARY"] = os.path.join(os.path.dirname(__file__), "external", "ffprobe.exe")




from pydub import AudioSegment

# Абсолютный путь к директории с файлами
base_dir = os.path.dirname(os.path.abspath(__file__))

# Пути к ffmpeg и ffprobe
ffmpeg_exec = os.path.join(base_dir, 'external', 'ffmpeg.exe')
ffprobe_exec = os.path.join(base_dir, 'external', 'ffprobe.exe')

# Указываем pydub, где искать ffmpeg и ffprobe
AudioSegment.converter = ffmpeg_exec
AudioSegment.ffprobe = ffprobe_exec

# Пути к файлам
input_file = os.path.join(base_dir, 'mp3', '1.mp3')
output_file = os.path.join(base_dir, 'mp3', '1.m4b')

def convert_mp3_to_m4b(input_path, output_path):
    # Загружаем MP3 файл
    audio = AudioSegment.from_mp3(input_path)

    # Конвертируем в M4B формат
    audio.export(output_path, format="mp4", codec="aac")
    print(f"Файл успешно конвертирован: {output_path}")

if __name__ == '__main__':
    convert_mp3_to_m4b(input_file, output_file)