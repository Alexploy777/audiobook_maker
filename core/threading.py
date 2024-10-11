from PyQt5.QtCore import QThread, pyqtSignal

from core import ConverterManager


class ConvertThread(QThread):
    progress_updated = pyqtSignal(int)
    # progress_description = pyqtSignal(str)
    # conversion_finished = pyqtSignal()

    def __init__(self, file_paths, output_path, bitrate, metadata):
        super().__init__()
        self.file_paths = file_paths
        self.output_path = output_path
        self.bitrate = bitrate
        self.metadata = metadata
        self.converter_manager = ConverterManager()

    def run(self):
        self.converter_manager.start(self.file_paths, self.output_path)
        # self.conversion_finished.emit()

    def update_progress_emit(self, progress):
        self.progress_updated.emit(progress)
    #
    # def update_progress_description(self, description):
    #     self.progress_description.emit(description)