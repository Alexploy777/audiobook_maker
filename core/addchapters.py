# core/addchapters.py
import os
import shutil
import subprocess
import tempfile


class AddChapters:
    def __init__(self, output_file, chapter_durations):
        self.output_file = output_file
        self.chapter_durations = chapter_durations

    def create_chapters_metadata(self):
        metadata_content = ";FFMETADATA1\n"
        current_time = 0
        for i, duration in enumerate(self.chapter_durations):
            start_time = current_time
            end_time = current_time + duration
            metadata_content += f"[CHAPTER]\nTIMEBASE=1/1\nSTART={int(start_time)}\nEND={int(end_time)}\ntitle=chapter_{i + 1:03}\n"
            current_time = end_time
        return metadata_content

    def add_chapters(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ffmetadata") as f:
            f.write(self.create_chapters_metadata().encode('utf-8'))
        metadata_file = f.name
        output_temp_file = tempfile.mktemp(suffix=".m4b")

        try:
            # Создаем временный файл с главами
            subprocess.run([
                "ffmpeg", "-i", self.output_file, "-i", metadata_file, "-map_metadata", "1", "-codec", "copy",
                output_temp_file
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
                creationflags=subprocess.CREATE_NO_WINDOW)

            # Заменяем оригинальный файл временным
            shutil.move(output_temp_file, self.output_file)
        finally:
            os.remove(metadata_file)
            if os.path.exists(output_temp_file):
                os.remove(output_temp_file)
