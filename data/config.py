# data/config.py
import json
import os

from PyQt5.QtWidgets import QMessageBox


class Config:
    WINDOWTITLE = 'Audiobook Maker'
    AUDIO_BITRATE = "128k"
    AUDIO_BITRATE_CHOICES = ['64k', '96k', '128k', '144k', '160k',
                             '192k', '256k', '320k']
    FFMPEG_PATH = "external"
    CONFIG_FILE = "config.json"
    ALLOWED_EXTENSIONS = ('.mp3',)
    AUDIO_CODEC = "aac"
    OUTPUT_FORMAT = "m4b"
    CHAPTER_MARKS = True
    COVER_IMAGE_FORMAT = "jpg"
    DELETE_TEMP_FILES = True
    DEFAULT_GENRE = "Audiobook"
    DEFAULT_AUTHOR = "Unknown"
    DEFAULT_TITLE = "Untitled"
    FFMPEG_LOG_LEVEL = "info"

    @classmethod
    def get_config_path(cls):
        CONFIG_DIR = os.path.join(os.getenv('APPDATA'), 'AudioBookMacker')
        CONFIG_PATH = os.path.join(CONFIG_DIR, cls.CONFIG_FILE)
        os.makedirs(CONFIG_DIR, exist_ok=True)
        return CONFIG_PATH

    @classmethod
    def load_config(cls):
        CONFIG_PATH = cls.get_config_path()
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    for key, value in config_data.items():
                        if hasattr(cls, key):
                            setattr(cls, key, value)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                QMessageBox.critical(None, "Ошибка", f"Ошибка загрузки конфигурации: {e}")

    @classmethod
    def set_audio_bitrate(cls, bitrate):
        cls.AUDIO_BITRATE = bitrate
        cls.save_config()

    @classmethod
    def save_config(cls):
        CONFIG_PATH = cls.get_config_path()
        config_data = {key: getattr(cls, key) for key in dir(cls) if
                       not key.startswith("__") and not callable(getattr(cls, key))}
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)


if __name__ == '__main__':
    pass
