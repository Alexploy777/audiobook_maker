# data/config.py
import json
import os


class Config:
    WINDOWTITLE = 'Audiobook Maker'
    AUDIO_BITRATE = "64k"
    AUDIO_BITRATE_CHOICES = ["64k", "128k", "256k", "320k", "512k"]
    AUDIO_CODEC = "aac"
    OUTPUT_FORMAT = "m4b"
    CHAPTER_MARKS = True
    COVER_IMAGE_FORMAT = "jpg"
    TEMP_DIR = "/tmp/audiobook_maker"
    DELETE_TEMP_FILES = True
    MAX_THREADS = 4
    DEFAULT_GENRE = "Audiobook"
    DEFAULT_AUTHOR = "Unknown"
    DEFAULT_TITLE = "Untitled"
    FFMPEG_PATH = "external/ffmpeg.exe"
    FFMPEG_LOG_LEVEL = "info"
    CONFIG_FILE = "config.json"

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
