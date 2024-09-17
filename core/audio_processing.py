# core/audio_processing.py
from pydub import AudioSegment


class AudioProcessor:
    def __init__(self, ffmpeg_path):
        AudioSegment.converter = ffmpeg_path

    def merge_mp3s(self, file_paths, update_progress):
        """Объединяет несколько MP3 файлов в один."""
        combined = AudioSegment.empty()

        num = int(100 / len(file_paths))

        for file_path in file_paths:
            combined += AudioSegment.from_mp3(file_path)
            num += num
            update_progress(num)

        return combined


    def convert_and_combine(self, file_paths, bitrate, update_progress):
        mp3_combined = self.merge_mp3s(file_paths, update_progress)
        with open('mp3_combined.mp3', 'wb') as f:
            mp3_combined.export(f, format='mp3', bitrate=bitrate)
        return update_progress(100)

