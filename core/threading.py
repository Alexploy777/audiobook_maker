from PyQt5.QtCore import QThread, pyqtSignal


class ConvertThread(QThread):
    progress_updated = pyqtSignal(int)
    progress_description = pyqtSignal(str)
    conversion_finished = pyqtSignal()

    def __init__(self, audio_processor, file_paths, output_path, bitrate, metadata):
        super().__init__()
        self.audio_processor = audio_processor
        self.file_paths = file_paths
        self.output_path = output_path
        self.bitrate = bitrate
        self.metadata = metadata

    def run(self):
        self.audio_processor.convert_and_combine(file_paths=self.file_paths, bitrate=self.bitrate, update_progress=self.update_progress, output_path=self.output_path, metadata=self.metadata, progress_description=self.update_progress_description)
        self.conversion_finished.emit()

    def update_progress(self, progress):
        self.progress_updated.emit(progress)

    def update_progress_description(self, description):
        self.progress_description.emit(description)