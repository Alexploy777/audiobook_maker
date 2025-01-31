import os
import re
import shutil
import subprocess
import tempfile
from io import StringIO


class AddChapters:
    def __init__(self, output_file, chapter_durations, my_signals=None):
        self.output_file = output_file
        self.chapter_durations = chapter_durations
        self.my_signals = my_signals
        self._init_signals()

    def _init_signals(self):
        """Инициализирует сигналы прогресса."""
        if self.my_signals:
            self.my_signals.progress_bar_signal.emit(0)
            self.my_signals.label_info_signal.emit("Добавляю главы..")
            self.my_signals.label_info_signal_2.emit("--<>--")

    def create_chapters_metadata(self):
        """Генерирует метаданные для глав в формате FFmpeg."""
        buffer = StringIO()
        buffer.write(";FFMETADATA1\n")
        current_time = 0.0

        for i, duration in enumerate(self.chapter_durations, 1):
            start = int(current_time)
            end = int(current_time + duration)
            buffer.write(
                f"[CHAPTER]\nTIMEBASE=1/1\nSTART={start}\nEND={end}\n"
                f"title=chapter_{i:03}\n\n"
            )
            current_time += duration

        return buffer.getvalue()

    def add_chapters(self):
        """Добавляет главы в аудиофайл через FFmpeg."""
        # Проверка наличия FFmpeg
        if not shutil.which("ffmpeg"):
            self._notify_error("FFmpeg не найден! Установите FFmpeg и добавьте его в PATH.")
            return False

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".ffmetadata", delete=False) as meta_file:
            metadata_content = self.create_chapters_metadata()
            meta_file.write(metadata_content)
            metadata_path = meta_file.name

        output_temp = tempfile.NamedTemporaryFile(suffix=".m4b", delete=False).name
        success = False

        try:
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",  # Перезапись без подтверждения
                "-i", self.output_file,
                "-i", metadata_path,
                "-map_metadata", "1",
                "-c", "copy",
                output_temp
            ]

            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            total_duration = sum(self.chapter_durations)
            progress_re = re.compile(r"time=(\d+):(\d{2}):(\d{2})\.\d{2}")

            while process.poll() is None:
                line = process.stdout.readline()
                if match := progress_re.search(line):
                    h, m, s = map(int, match.groups())
                    current = h * 3600 + m * 60 + s
                    progress = int((current / total_duration) * 100) if total_duration > 0 else 0
                    self._update_progress(progress)

            if process.returncode == 0:
                shutil.move(output_temp, self.output_file)
                success = True
                self._notify_success()
            else:
                self._notify_error(f"FFmpeg error (code {process.returncode})")

        except Exception as e:
            self._notify_error(f"Critical error: {str(e)}")
        finally:
            self._cleanup(metadata_path, output_temp)
            return success

    def _update_progress(self, value):
        """Обновляет прогресс через сигналы."""
        if self.my_signals:
            self.my_signals.progress_bar_signal.emit(value)

    def _notify_success(self):
        """Уведомляет об успешном завершении."""
        if self.my_signals:
            self.my_signals.label_info_signal.emit(
                f"Главы успешно добавлены в {os.path.basename(self.output_file)}"
            )

    def _notify_error(self, message):
        """Уведомляет об ошибке."""
        if self.my_signals:
            self.my_signals.label_info_signal.emit(f"Ошибка: {message}")

    def _cleanup(self, *files):
        """Удаляет временные файлы."""
        for path in files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                self._notify_error(f"Cleanup failed: {str(e)}")
