import os
import subprocess
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThreadPool, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QMessageBox, QSystemTrayIcon, QMenu, QAction, QTabWidget, QVBoxLayout, QHBoxLayout
)

from gui import WidgetReplacer, TableViewManager, Ui_MainWindow, CustomListWidget
from utils import CheckChapters, Timer
from core import MetadataManager, ConverterSignals, Converter, M4bMerger
from data import Config, FileManager

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class AudiobookCreator(QMainWindow, Ui_MainWindow):
    file_paths = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._load_config()
        self._init_ui()
        self._init_converter_manager()
        self._init_tray_icon()

        self.file_manager = FileManager(self)
        self.metadata_manager = MetadataManager(self.label_cover_of_book)
        self.timer = Timer(self.lcdNumber)
        self.tableviewmanager = TableViewManager(self.tableView, ['Имя главы', 'Время начала'])
        self.checkchapters = CheckChapters(self.tableviewmanager)

        self.output_path = ''
        self.progressBar.setValue(0)

    def _load_config(self):
        """Загружает конфигурацию и настраивает окно."""
        Config.load_config()
        self.setWindowTitle(Config.WINDOWTITLE)
        self.setWindowIcon(QIcon("Audiobook2.png"))
        self.allowed_extensions = tuple(Config.ALLOWED_EXTENSIONS)

    def _init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        self.newListWidget = CustomListWidget(self.allowed_extensions)
        self.newListWidget.setFrameShape(QtWidgets.QFrame.NoFrame)

        replacer = WidgetReplacer(self.tabWidget)
        replacer.replace_widget(self.listWidget, self.newListWidget)

        self.comboBox_audio_quality.addItems(Config.AUDIO_BITRATE_CHOICES)
        self.comboBox_audio_quality.setCurrentText(Config.AUDIO_BITRATE)
        self.comboBox_audio_quality.currentTextChanged.connect(self.update_audio_bitrate)

        self.pushButton.clicked.connect(self.add_files)
        self.newListWidget.itemSelectionChanged.connect(self.display_metadata)
        self.pushButton_2.clicked.connect(self.remove_selected_files)
        self.pushButton_upload_cover.clicked.connect(self.upload_cover)
        self.pushButton_convert.clicked.connect(self.start_conversion)
        self.pushButton_stop_and_clean.clicked.connect(self.cleann_all)
        self.pushButton_openDir.clicked.connect(self.open_folder_with_file)

    def _init_converter_manager(self):
        """Инициализирует менеджер конвертации."""
        os.environ['PATH'] += os.pathsep + os.path.abspath(Config.FFMPEG_PATH)
        self.thread_pool = QThreadPool()
        self.audibook_converter_signals = ConverterSignals()
        self.audibook_converter_signals.label_info_signal.connect(self.update_label)
        self.audibook_converter_signals.label_info_signal_2.connect(self.update_label_2)
        self.audibook_converter_signals.all_tasks_completed.connect(self.on_all_tasks_completed)
        self.audibook_converter_signals.progress_bar_signal.connect(self.update_progress)

    def _init_tray_icon(self):
        """Инициализирует иконку в системном трее."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("Audiobook2.png"))

        tray_menu = QMenu()
        show_action = QAction("Открыть", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def get_files(self):
        """Возвращает список выбранных файлов."""
        return [self.newListWidget.item(i).text() for i in range(self.newListWidget.count())]

    def open_folder_with_file(self):
        """Открывает папку с выходным файлом."""
        if folder_path := os.path.dirname(self.output_path):
            self.showMinimized()
            if sys.platform == "win32":
                subprocess.Popen(f'explorer /select,"{os.path.normpath(self.output_path)}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", self.output_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])

    def update_audio_bitrate(self, bitrate):
        """Обновляет битрейт аудио."""
        Config.set_audio_bitrate(bitrate)

    def add_files(self):
        """Добавляет файлы в список."""
        self.file_manager.add_files(self.newListWidget)

    def remove_selected_files(self):
        """Удаляет выбранные файлы из списка."""
        self.file_manager.remove_files(self.newListWidget)

    def cleann_all(self):
        """Очищает все поля и сбрасывает состояние."""
        self.newListWidget.clear()
        self.timer.reset_timer()
        self.metadata_manager.clear_metadata(*self.get_metadata_widgets())
        self.progressBar.setValue(0)
        self.update_label('Добавь файлы для создания новой книги')
        self.update_label_2('Или брось целиком папку в окно')
        self.tabWidget.setCurrentIndex(0)
        self.tableviewmanager.clean()

    def display_metadata(self):
        """Отображает метаданные выбранного файла."""
        if selected_items := self.newListWidget.selectedItems():
            file_path = selected_items[0].text()
            metadata, audio = self.metadata_manager.extract_metadata(file_path)
            self.lineEdit_title.setText(metadata["title"])
            self.lineEdit_artist.setText(metadata["artist"])
            self.lineEdit_album.setText(metadata["album"])
            self.lineEdit_year.setText(metadata["year"])
            self.lineEdit_genre.setText(metadata["genre"])
            self.lineEdit_albumartist.setText(metadata["albumartist"])
            self.metadata_manager.extract_and_show_cover(audio, self.label_cover_of_book)

    def upload_cover(self):
        """Загружает обложку для аудиокниги."""
        cover_image_path = self.file_manager.upload_cover()
        self.metadata_manager.show_cover_image_path(cover_image_path)

    def checking_all_data(self):
        """Проверяет, все ли данные готовы для конвертации."""
        self.output_path = self.file_manager.get_output_file_path()
        self.audibook_converter_signals.label_info_signal_2.emit(f'{self.output_path}')

        # Исправлено: разделено присваивание и проверка
        self.file_paths = self.get_files()
        if not self.file_paths:
            QMessageBox.warning(self, "Предупреждение", "Не выбраны файлы для аудиокниги")
            return False
        return bool(self.output_path and self.file_paths)

    def start_conversion(self):
        """Запускает процесс конвертации."""
        if self.checking_all_data():
            self.timer.reset_timer()
            self.timer.start_timer()
            self.label_progress_description_2.clear()
            self.audibook_converter_signals.label_info_signal.emit('Запустил конвертацию..')

            metadata = {
                'title': self.lineEdit_title.text(),
                'artist': self.lineEdit_artist.text(),
                'album': self.lineEdit_album.text(),
                'year': self.lineEdit_year.text(),
                'genre': self.lineEdit_genre.text(),
                'albumartist': self.lineEdit_albumartist.text(),
            }
            self.metadata = metadata

            self.completed_tasks = 0
            self.progressBar.setValue(0)
            self.quantity = len(self.file_paths)
            self.output_temp_files_list = [None] * self.quantity

            for index, file in enumerate(self.file_paths):
                task = Converter(
                    index=index,
                    quantity=self.quantity,
                    file=file,
                    output_temp_files_list=self.output_temp_files_list,
                    bitrate=Config.AUDIO_BITRATE
                )
                task.my_signals.progress_bar_signal.connect(self.update_progress)
                task.my_signals.label_info_signal.connect(self.update_label)
                task.my_signals.label_info_signal_2.connect(self.update_label_2)
                self.thread_pool.start(task)

    def update_label(self, value):
        """Обновляет текстовую метку."""
        max_length = 60
        self.label_progress_description.setText(value[:max_length] + '...' if len(value) > max_length else value)

    def update_label_2(self, value):
        """Обновляет вторую текстовую метку."""
        max_length = 90
        self.label_progress_description_2.setText(value[:max_length] + '...' if len(value) > max_length else value)

    def update_progress(self):
        """Обновляет прогрессбар."""
        self.completed_tasks += 1
        self.progressBar.setValue(int((self.completed_tasks / self.quantity) * 100))
        if self.completed_tasks == self.quantity:
            self.audibook_converter_signals.all_tasks_completed.emit()

    def on_all_tasks_completed(self):
        """Обрабатывает завершение всех задач."""
        self.temp_files_list = [f.name for f in self.output_temp_files_list if f is not None]
        self.audibook_converter_signals.label_info_signal.emit('Все файлы успешно конвертированы!')
        self.audibook_converter_signals.label_info_signal_2.emit('Запускаю объединение файлов..')

        m4bmerger = M4bMerger(self.temp_files_list, self.output_path, self.metadata)
        m4bmerger.my_signals.signal_complete_merge.connect(self.end_of_merge)
        m4bmerger.my_signals.progress_bar_signal.connect(self.update_progress)
        m4bmerger.my_signals.label_info_signal.connect(self.update_label)
        m4bmerger.my_signals.label_info_signal_2.connect(self.update_label_2)
        self.thread_pool.start(m4bmerger)

    def end_of_merge(self):
        """Завершает процесс объединения файлов."""
        self.delete_temp_files(self.temp_files_list)
        self.audibook_converter_signals.label_info_signal.emit(f'Работа завершена, файл аудиокниги здесь:')
        self.audibook_converter_signals.label_info_signal_2.emit(f'{self.output_path}')
        self.progressBar.setValue(100)
        self.timer.stop_timer()
        self.checkchapters.checkChapters(self.output_path)
        self.tabWidget.setCurrentIndex(1)

    def delete_temp_files(self, temp_files_list):
        """Удаляет временные файлы."""
        for temp_file in temp_files_list:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudiobookCreator()
    window.show()
    sys.exit(app.exec_())