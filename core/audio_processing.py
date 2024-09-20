# core/audio_processing.py
import os

from pydub import AudioSegment


class AudioProcessor:
    def __init__(self, ffmpeg_path):
        AudioSegment.converter = ffmpeg_path


    # точка входа
    def convert_and_combine(self, file_paths, bitrate, update_progress):
        total_progress_bar_steps = 100 // (len(file_paths))
        progress_bar_steps = 0
        converted_files = []
        if not os.path.exists("temp"):
            os.makedirs("temp")
        for index, file_path in enumerate(file_paths):
            temp_output = 'temp/tmp_' + os.path.splitext(os.path.basename(file_path))[0] + '.m4b'
            self.convert_file_to_m4b(file_path, temp_output, bitrate)
            converted_files.append(temp_output)
            progress_bar_steps += total_progress_bar_steps
            update_progress(progress_bar_steps)



    def convert_file_to_m4b(self, file_path, temp_output, bitrate):
        audio = AudioSegment.from_mp3(file_path)
        audio.export(temp_output, format="mp4", bitrate=bitrate, codec="aac")