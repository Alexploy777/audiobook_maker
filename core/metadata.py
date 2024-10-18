# data/metadata.py
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox
from mutagen.id3 import ID3
from mutagen.mp3 import MP3


class MetadataManager:
    metadata = {}

    def __init__(self, label_cover_of_book):
        self.label_cover_of_book = label_cover_of_book

    @staticmethod
    def clear_metadata(*args):
        for widget in args:
            widget.clear()

    # @staticmethod
    def extract_metadata(self, file_path):
        metadata = {
            "title": "",
            "artist": "",
            "album": "",
            "year": "",
            "genre": "",
            "albumartist": "",
        }
        try:
            audio = MP3(file_path, ID3=ID3)
            metadata = {
                "title": str(audio.get("TIT2", "Unknown Title").text[0]),
                "artist": str(audio.get("TPE1", "Unknown Artist").text[0]),
                "album": str(audio.get("TALB", "Unknown Album").text[0]),
                "genre": str(audio.get("TCON", "Unknown Genre").text[0]),
                "year": str(audio.get("TDRC", "Unknown Year").text[0]),
                "albumartist": str(audio.get("TPE2", "Unknown Album Artist").text[0]),
            }
            self.metadata = metadata
            return metadata, audio
        except Exception as e:
            QMessageBox.warning(None, "Ошибка", f"Исключение {e.args[0]}")
            return metadata, None

    def show_cover_image(self, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        if pixmap.isNull():
            QMessageBox.warning(None, "Ошибка", "Не удалось загрузить изображение обложки.")
        else:
            self.label_cover_of_book.setPixmap(
                pixmap.scaled(
                    self.label_cover_of_book.size(),
                    aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio
                )
            )
            self.metadata['image_data'] = image_data

    def show_cover_image_path(self, cover_image_path):
        if cover_image_path:
            with open(cover_image_path, 'rb') as f:
                image_data = f.read()
            self.show_cover_image(image_data)

    def extract_and_show_cover(self, audio, label_cover_of_book):
        if audio is None:
            label_cover_of_book.clear()
            return
        try:
            image_data = audio.tags.getall('APIC')[0].data
            self.show_cover_image(image_data)
        except IndexError:
            label_cover_of_book.clear()
            QMessageBox.information(None, "Информация", "Обложка не найдена в выбранном файле.")
