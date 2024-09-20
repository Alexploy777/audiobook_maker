# core/audio_processing.py
import os

from mutagen.mp4 import MP4, MP4Cover
from pydub import AudioSegment


class AudioProcessor:
    def __init__(self, ffmpeg_path):
        AudioSegment.converter = ffmpeg_path


    # точка входа
    def convert_and_combine(self, file_paths, bitrate, update_progress, output_path, metadata):
        self.total_progress_bar_steps = 100 // (len(file_paths))
        progress_bar_steps = 0
        update_progress(progress_bar_steps)
        converted_files = []
        if not os.path.exists("temp"):
            os.makedirs("temp")
        for index, file_path in enumerate(file_paths):
            temp_output = 'temp/tmp_' + os.path.splitext(os.path.basename(file_path))[0] + '.m4b'
            self.convert_file_to_m4b(file_path, temp_output, bitrate)
            converted_files.append(temp_output)
            progress_bar_steps = (index + 1) * self.total_progress_bar_steps
            update_progress(progress_bar_steps)

        # Объединение всех временных m4b файлов
        self.combine_files(converted_files, output_path, update_progress)

        for temp_file in converted_files:
            os.remove(temp_file)

        # Добавление метаданных и обложки
        self.add_cover_and_metadata(output_path, metadata, update_progress)
        update_progress(100)

    def convert_file_to_m4b(self, file_path, temp_output, bitrate):
        audio = AudioSegment.from_mp3(file_path)
        audio.export(temp_output, format="mp4", bitrate=bitrate, codec="aac")

    def combine_files(self, converted_files, output_path, update_progress):
        update_progress(1)
        combined = AudioSegment.empty()

        for index, file_path in enumerate(converted_files):
            audio = AudioSegment.from_file(file_path, format="mp4")
            combined += audio

            progress_bar_steps = (index + 1) * self.total_progress_bar_steps
            update_progress(progress_bar_steps)

        update_progress(1)
        combined.export(output_path, format="mp4", codec="aac") # долго, нет индикации в прогресс-баре

    def add_cover_and_metadata(self, output_path, metadata, update_progress):
        audio = MP4(output_path)

        update_progress(1)

        # Добавление метаданных
        audio['\xa9nam'] = metadata.get("title")
        audio['\xa9ART'] = metadata.get("artist")
        audio['\xa9alb'] = metadata.get("album")
        audio['\xa9day'] = metadata.get("year")
        audio['\xa9gen'] = metadata.get("genre")

        update_progress(50)

        if cover_image_bytes := metadata.get('image_data'):
            cover = MP4Cover(cover_image_bytes, imageformat=MP4Cover.FORMAT_JPEG)
            audio['covr'] = [cover]

        update_progress(90)

        audio.save()
