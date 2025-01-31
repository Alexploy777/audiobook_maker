import os
import shutil
import subprocess
import tempfile
import logging
from typing import Optional

from PyQt5.QtCore import QRunnable, pyqtSlot
from data import Config
from .convertersignals import ConverterSignals


class Converter(QRunnable):
    def __init__(
            self,
            index: int,
            quantity: int,
            file: str,
            output_temp_files_list: list,
            bitrate: str
    ):
        super().__init__()
        self.index = index
        self.quantity = quantity
        self.file_path = file
        self.output_temp_files_list = output_temp_files_list
        self.bitrate = bitrate
        self.my_signals = ConverterSignals()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Конфигурационные параметры
        self.audio_codec = Config.AUDIO_CODEC
        self.output_format = f'.{Config.OUTPUT_FORMAT}'
        self.ffmpeg_timeout = 30  # Таймаут выполнения в секундах

    @pyqtSlot()
    def run(self) -> None:
        """Основной метод выполнения задачи конвертации."""
        try:
            self._validate_inputs()
            output_file = self._convert_file()

            if output_file and os.path.exists(output_file.name):
                self.output_temp_files_list[self.index] = output_file
                progress = self.index
                self._emit_progress(progress, "Файл конвертирован:", self.file_path)
            else:
                self._emit_error("Ошибка конвертации", self.file_path)

        except Exception as e:
            self.logger.exception(f"Критическая ошибка: {str(e)}")
            self._emit_error("Критическая ошибка", str(e))

    def _validate_inputs(self) -> None:
        """Проверка валидности входных данных."""
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"Файл не существует: {self.file_path}")

        if not shutil.which("ffmpeg"):
            raise EnvironmentError("FFmpeg не найден в системном PATH")

    def _convert_file(self) -> Optional[tempfile.NamedTemporaryFile]:
        """Выполняет конвертацию файла через FFmpeg."""
        try:
            with tempfile.NamedTemporaryFile(
                    suffix=self.output_format,
                    delete=False
            ) as output_buffer:
                pass  # Файл создается и сразу закрывается для FFmpeg

            command = [
                'ffmpeg',
                '-i', self.file_path,
                '-vn',  # Игнорировать видео потоки
                '-c:a', self.audio_codec,
                '-b:a', self.bitrate,
                '-y',  # Перезаписать без подтверждения
                '-hide_banner',  # Скрыть служебную информацию
                '-loglevel', 'error',  # Только ошибки
                output_buffer.name
            ]

            result = subprocess.run(
                command,
                timeout=self.ffmpeg_timeout,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                encoding='utf-8',
                errors='replace'
            )

            self.logger.debug(f"Конвертация успешна: {self.file_path}")
            return output_buffer

        except subprocess.TimeoutExpired:
            self.logger.error(f"Таймаут конвертации: {self.file_path}")
            os.remove(output_buffer.name)
            return None

        except subprocess.CalledProcessError as e:
            error_msg = f"Ошибка FFmpeg ({e.returncode}): {e.stderr}"
            self.logger.error(error_msg)
            os.remove(output_buffer.name)
            return None

        except Exception as e:
            self.logger.error(f"Ошибка конвертации: {str(e)}")
            if os.path.exists(output_buffer.name):
                os.remove(output_buffer.name)
            return None

    def _emit_progress(self, progress: int, message: str, details: str) -> None:
        """Отправляет сигналы об успешном прогрессе."""
        self.my_signals.progress_bar_signal.emit(progress)
        self.my_signals.label_info_signal.emit(message)
        self.my_signals.label_info_signal_2.emit(details)

    def _emit_error(self, message: str, details: str) -> None:
        """Отправляет сигналы об ошибке."""
        self.my_signals.label_info_signal.emit(f"{message}: {details}")
        self.my_signals.label_info_signal_2.emit("Операция прервана")
        self.my_signals.progress_bar_signal.emit(-1)
