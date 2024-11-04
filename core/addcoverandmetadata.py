from mutagen.mp4 import MP4, MP4Cover

from .convertersignals import ConverterSignals


class AddCoverAndMetadata:
    def __init__(self, output_file, metadata):
        self.my_signals = ConverterSignals()
        self.output_file = output_file
        self.metadata = metadata

    def add_cover_and_metadata(self):
        self.my_signals.label_info_signal.emit('Добавляю метаданные')
        self.my_signals.progress_bar_signal.emit(60)
        audio = MP4(self.output_file)

        # Добавление метаданных
        audio['\xa9nam'] = self.metadata.get("title")
        audio['\xa9ART'] = self.metadata.get("artist")
        audio['\xa9alb'] = self.metadata.get("album")
        audio['\xa9day'] = self.metadata.get("year")
        audio['\xa9gen'] = self.metadata.get("genre")

        if cover_image_bytes := self.metadata.get('image_data'):
            cover = MP4Cover(cover_image_bytes, imageformat=MP4Cover.FORMAT_JPEG)
            audio['covr'] = [cover]
        self.my_signals.progress_bar_signal.emit(90)
        self.my_signals.label_info_signal.emit('Сохраняю файл')
        audio.save()
