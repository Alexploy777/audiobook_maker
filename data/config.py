# data/config.py
import json
import os


class Config:
    WINDOWTITLE = 'Audiobook Maker'
    AUDIO_BITRATE = "128k"
    AUDIO_BITRATE_CHOICES = ['64k', '96k', '128k', '144k', '160k',
                             '192k', '256k', '320k']
    FFMPEG_PATH = "external"
    CONFIG_FILE = "config.json"
    ALLOWED_EXTENSIONS = ('.mp3')
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
    def load_config(cls):
        if os.path.exists(cls.CONFIG_FILE):
            with open(cls.CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
                for key, value in config_data.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)

    @classmethod
    def set_audio_bitrate(cls, bitrate):
        cls.AUDIO_BITRATE = bitrate
        cls.save_config()

    @classmethod
    def save_config(cls):
        config_data = {key: getattr(cls, key) for key in dir(cls) if not key.startswith("__") and not callable(getattr(cls, key))}
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
