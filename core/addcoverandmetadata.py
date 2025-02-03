from mutagen.mp4 import MP4, MP4Cover
from typing import Optional, Dict, Any
import imghdr
import logging


class AddCoverAndMetadata:
    # Соответствие между тегами MP4 и ключами метаданных
    TAG_MAP = {
        'title': '\xa9nam',  # Название трека
        'artist': '\xa9ART',  # Исполнитель
        'album': '\xa9alb',  # Альбом
        'genre': '\xa9gen',  # Жанр
        'year': '\xa9day',  # Дата/год
        'albumartist': 'aART'  # Исполнитель альбома
    }

    def __init__(self, output_file: str, metadata: Dict[str, Any], my_signals: Optional[object] = None):
        self.my_signals = my_signals
        self.output_file = output_file
        self.metadata = metadata
        self.logger = logging.getLogger(self.__class__.__name__)

    def _update_progress(self, value: int, message: str = "", message2: str = "") -> None:
        if self.my_signals:
            if value >= 0:
                # self.my_signals.progress_bar_signal.emit(value)
                self.my_signals.progress_bar_signal_m4bmerger.emit(value)
            if message:
                self.my_signals.label_info_signal.emit(message)
            if message2:
                self.my_signals.label_info_signal_2.emit(message2)

    def _load_audio_file(self) -> Optional[MP4]:
        try:
            return MP4(self.output_file)
        except Exception as e:
            error_msg = f"Ошибка загрузки файла: {str(e)}"
            self.logger.error(error_msg)
            self._update_progress(-1, error_msg, "Файл не найден или поврежден")
            return None

    def _set_basic_metadata(self, audio: MP4) -> None:
        """Установка основных метаданных"""
        for key, tag in self.TAG_MAP.items():
            if value := self.metadata.get(key):
                audio[tag] = [value]
                self.logger.debug(f"Установлен тег {tag}: {value}")

    def _add_cover_image(self, audio: MP4) -> None:
        """Добавление обложки"""
        if not (image_data := self.metadata.get('image_data')):
            return

        try:
            image_format = imghdr.what(None, image_data)
            format_map = {
                'jpeg': MP4Cover.FORMAT_JPEG,
                'png': MP4Cover.FORMAT_PNG
            }

            if image_format not in format_map:
                raise ValueError(f"Неподдерживаемый формат: {image_format}")

            audio.tags['covr'] = [MP4Cover(image_data, format_map[image_format])]
            self.logger.info("Обложка добавлена")
        except Exception as e:
            error_msg = f"Ошибка добавления обложки: {str(e)}"
            self.logger.error(error_msg)
            self._update_progress(-1, error_msg)

    def add_cover_and_metadata(self) -> bool:
        self._update_progress(0, "Начало обработки метаданных", "======")

        if not (audio := self._load_audio_file()):
            return False

        try:
            self._update_progress(30, "Добавление метаданных")
            self._set_basic_metadata(audio)

            self._update_progress(60, "Добавление обложки")
            self._add_cover_image(audio)

            self._update_progress(90, "Сохранение изменений")
            audio.save()

            self._update_progress(100, "Метаданные добавлены", self.output_file)
            return True

        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            self.logger.exception(error_msg)
            self._update_progress(-1, error_msg, "Операция прервана")
            return False
