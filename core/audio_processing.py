# core/audio_processing.py
from pydub import AudioSegment


class AudioProcessor:
    def __init__(self, ffmpeg_path):
        AudioSegment.converter = ffmpeg_path


    def convert_and_combine(self, file_paths, output_path, bitrate, metadata, update_progress):
        pass