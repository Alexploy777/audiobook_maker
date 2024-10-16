# main.py
import os
import sys

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox  # Импортируем класс QMainWindow и QApplication

# from core import AudioProcessor, Converter, ConverterSignals  # Подключаем AudioProcessor из core/audio_processing.py
# from core import ConverterManager
from core import MetadataManager, ConverterSignals, Converter  # Подключаем MetadataManager из core/metadata.py
from data import Config  # Подключаем Config из data/config
from data import FileManager  # Подключаем FileManager из data/file_manager
from gui import Ui_MainWindow  # Подключаем класс MainWindow из gui.py
# from core import ConvertThread # Подключаем класс ConvertThread из core/convert_thread.py


class AudiobookCreator(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(AudiobookCreator, self).__init__()
        self.setupUi(self)
        Config.load_config()  # Загружаем конфигурацию при запуске приложения

        self.setWindowTitle(Config.WINDOWTITLE)

        self.file_manager = FileManager()
        self.metadata_manager = MetadataManager(self.label_cover_of_book)
        # self.audio_processor = AudioProcessor(ffmpeg_path=Config.FFMPEG_PATH)  # Укажите путь к ffmpeg

        self.progressBar.setValue(1)  # Устанавливаем начальное значение

        self.init_ui()
        self.convertermanager()

    def init_ui(self):
        self.comboBox_audio_quality.addItems(Config.AUDIO_BITRATE_CHOICES)  # Добавляем варианты битрейта
        self.comboBox_audio_quality.setCurrentText(Config.AUDIO_BITRATE)  # Устанавливаем текущее значение из Config
        self.comboBox_audio_quality.currentTextChanged.connect(self.update_audio_bitrate)  # connect - при выборе другого битрейта
        self.pushButton.clicked.connect(self.add_files)  # connect - для добавления файлов
        self.listWidget.itemSelectionChanged.connect(self.display_metadata)  # При выборе/выделении файла
        self.pushButton_2.clicked.connect(self.remove_selected_files)  # connect - для удаления выделенных файлов
        self.pushButton_upload_cover.clicked.connect(self.upload_cover)  # connect - для загрузки обложки пользователя
        self.pushButton_convert.clicked.connect(self.start_conversion)  # connect - для конвертации
        self.pushButton_stop_and_clean.clicked.connect(self.stop_and_clean)  # connect - для остановки конвертации

    def convertermanager(self):
        self.progressBar.setValue(0)
        self.thread_pool = QThreadPool()
        self.completed_tasks = 0  # Количество завершённых задач

        self.output_temp_files_list = []  # Список для хранения временных файлов аудиофайлов

        # Дополнительный сигнал завершения всех задач
        self.all_tasks_completed_signal = ConverterSignals()
        self.all_tasks_completed_signal.all_tasks_completed.connect(self.on_all_tasks_completed)

    def get_metadata_widgets(self):
        return (
            self.lineEdit_title,
            self.lineEdit_artist,
            self.lineEdit_album,
            self.lineEdit_year,
            self.lineEdit_genre,
            self.label_cover_of_book
        )

    @staticmethod
    def update_audio_bitrate(bitrate):
        Config.set_audio_bitrate(bitrate)

    def add_files(self):
        self.file_manager.add_files(self.listWidget)

    def remove_selected_files(self):
        if self.file_manager.remove_files(self.listWidget):
            self.metadata_manager.clear_metadata(*self.get_metadata_widgets())

    def display_metadata(self):
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            self.metadata_manager.clear_metadata(*self.get_metadata_widgets())
            return

        file_path = selected_items[0].text()
        metadata, audio = self.metadata_manager.extract_metadata(file_path)
        self.lineEdit_title.setText(metadata["title"])
        self.lineEdit_artist.setText(metadata["artist"])
        self.lineEdit_album.setText(metadata["album"])
        self.lineEdit_year.setText(metadata["year"])
        self.lineEdit_genre.setText(metadata["genre"])

        self.metadata_manager.extract_and_show_cover(audio, self.label_cover_of_book)

    def upload_cover(self):
        cover_image_path = self.file_manager.upload_cover()
        self.metadata_manager.show_cover_image_path(cover_image_path)

    # def update_progress(self, progress):
    #     self.progressBar.setValue(progress)

    # def progress_description(self, description):
    #     self.label_progress_description.setText(description)

    # def conversion_finished(self):
    #     QMessageBox.information(self, "Готово", "Конвертация завершена!")
    #     self.progressBar.setValue(0)

    def stop_and_clean(self):
        pass



    def start_conversion(self):
        file_paths = self.file_manager.file_paths # Возвращает список файлов для конвертации
        output_path = self.file_manager.get_output_file_path()
        bitrate = Config.AUDIO_BITRATE

        metadata = self.metadata_manager.metadata
        metadata['title'] = self.lineEdit_title.text()
        metadata['artist'] = self.lineEdit_artist.text()
        metadata['album'] = self.lineEdit_album.text()
        metadata['year'] = self.lineEdit_year.text()
        metadata['genre'] = self.lineEdit_genre.text()

        # на этом этапе будем передавать аргументы и запускать конвертацию!!!
        # self.audio_processor, file_paths=file_paths, output_path=output_path, bitrate=bitrate, metadata=metadata

        # converter_manager = ConverterManager(self) # передали весь интервейс при инициации класса
        # # converter_manager.start_my_task(file_paths, output_path) # потом!
        # converter_manager.start_my_task(file_paths)

        print('Конвертация запущена')
        self.completed_tasks = 0  # Сбрасываем счетчик выполненных задач
        self.progressBar.setValue(0)  # Сбрасываем прогрессбар
        self.quantity = len(file_paths)
        self.output_temp_files_list = [None] * self.quantity  # Инициализируем список с None для каждого файла

        # Запускаем задачи
        for index, file in enumerate(file_paths):
            some_task = Converter(index=index, quantity=self.quantity, file=file,
                                  output_temp_files_list=self.output_temp_files_list)
            some_task.my_signals.progress_bar_signal.connect(self.update_progress)
            some_task.my_signals.label_info_signal.connect(self.update_label)
            self.thread_pool.start(some_task)


    def update_label(self, value):
        self.label_progress_description.setText(value)


    def update_progress(self, v):
        """Обновляет прогрессбар на основании выполнения задач."""
        self.completed_tasks += 1  # Увеличиваем количество завершённых задач
        progress_percentage = int((self.completed_tasks / self.quantity) * 100)  # Рассчитываем процент
        self.progressBar.setValue(progress_percentage)

        # Если все задачи завершены, отправляем сигнал
        if self.completed_tasks == self.quantity:
            self.all_tasks_completed_signal.all_tasks_completed.emit()

    def on_all_tasks_completed(self):
        """Вызывается при завершении всех задач."""
        temp_files_list = [f.name for f in self.output_temp_files_list]
        print(temp_files_list)
        QMessageBox.information(None, "Завершено", "Все задания выполнены!")
        self.delete_temp_files(temp_files_list)

    def delete_temp_files(self, temp_files_list):
        for temp_file in temp_files_list:
            if temp_file:
                os.remove(temp_file)  # Удаляем временный файл




if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AudiobookCreator()
    w.show()
    sys.exit(app.exec_())
