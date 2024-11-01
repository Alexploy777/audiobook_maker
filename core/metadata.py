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

            # Для каждого тега проверяется наличие и извлечение значения с использованием get
            metadata["title"] = str(audio.get("TIT2", [""])[0])
            metadata["artist"] = str(audio.get("TPE1", [""])[0])
            metadata["album"] = str(audio.get("TALB", [""])[0])
            metadata["genre"] = str(audio.get("TCON", [""])[0])
            metadata["year"] = str(audio.get("TDRC", [""])[0])
            metadata["albumartist"] = str(audio.get("TPE2", [""])[0])

            self.metadata = metadata
            return metadata, audio

        except Exception as e:
            QMessageBox.warning(None, "Ошибка", f"Произошло исключение: {str(e)}")
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


if __name__ == '__main__':
    pass
