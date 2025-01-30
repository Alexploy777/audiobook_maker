# audiobooksmaker.py
import os
import subprocess
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon

from gui import WidgetReplacer, TableViewManager
from utils import CheckChapters

os.environ['PATH'] += os.pathsep + os.path.abspath('external')

from PyQt5.QtCore import QThreadPool, QTimer, QTime, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, \
    QWidget, QSystemTrayIcon, QMenu, QAction  # Импортируем класс QMainWindow и QApplication
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QMainWindow
from core import MetadataManager, ConverterSignals, Converter, \
    M4bMerger  # Подключаем MetadataManager из core/metadata.py
from data import Config  # Подключаем Config из data/config
from data import FileManager  # Подключаем FileManager из data/file_manager
from gui import Ui_MainWindow, CustomListWidget  # Подключаем класс MainWindow из gui.py
from utils import Timer


class AudiobookCreator(QMainWindow, Ui_MainWindow):
    file_paths = []

    def __init__(self):
        super(AudiobookCreator, self).__init__()
        self.setupUi(self)
        config_instance = Config()
        Config.load_config()  # Загружаем конфигурацию при запуске приложения
        self.setWindowTitle(Config.WINDOWTITLE)
        self.allowed_extensions = tuple(Config.ALLOWED_EXTENSIONS)
        self.setWindowIcon(QIcon("Audiobook2.png"))
        self.init_tray_icon()

        self.file_manager = FileManager(self)
        self.metadata_manager = MetadataManager(self.label_cover_of_book)
        self.progressBar.setValue(0)  # Устанавливаем начальное значение
        self.init_ui()
        self.init_convertermanager()
        self.timer = Timer(self.lcdNumber)
        self.tableviewmanager = TableViewManager(self.tableView, ['Имя главы', 'Время начала'])
        self.checkchapters = CheckChapters(self.tableviewmanager)

        self.output_path = ''

    def init_tray_icon(self):
        # Создаем объект QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("Audiobook2.png"))  # Устанавливаем иконку для трея

        # Создаем меню для трея
        tray_menu = QMenu()

        # Добавляем действия в меню
        show_action = QAction("Открыть", self)
        show_action.triggered.connect(self.show)  # Показываем окно при выборе
        tray_menu.addAction(show_action)

        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(QApplication.quit)  # Полностью завершает приложение
        tray_menu.addAction(quit_action)

        # Присоединяем меню к иконке
        self.tray_icon.setContextMenu(tray_menu)

        # Отображаем иконку в трее
        self.tray_icon.show()

    def init_ui(self):
        self.newListWidget = CustomListWidget(self.allowed_extensions)
        self.newListWidget.setFrameShape(QtWidgets.QFrame.NoFrame)

        # replace_widget(self.tabWidget, self.listWidget, self.newListWidget)
        replacer = WidgetReplacer(self.tabWidget)
        replacer.replace_widget(self.listWidget, self.newListWidget)

        self.comboBox_audio_quality.addItems(Config.AUDIO_BITRATE_CHOICES)  # Добавляем варианты битрейта
        self.comboBox_audio_quality.setCurrentText(Config.AUDIO_BITRATE)  # Устанавливаем текущее значение из Config
        self.comboBox_audio_quality.currentTextChanged.connect(
            self.update_audio_bitrate)  # connect - при выборе другого битрейта
        self.pushButton.clicked.connect(self.add_files)  # connect - для добавления файлов
        self.newListWidget.itemSelectionChanged.connect(self.display_metadata)  # При выборе/выделении файла
        self.pushButton_2.clicked.connect(self.remove_selected_files)  # connect - для удаления выделенных файлов
        self.pushButton_upload_cover.clicked.connect(self.upload_cover)  # connect - для загрузки обложки пользователя
        self.pushButton_convert.clicked.connect(self.start_conversion)  # connect - для конвертации
        self.pushButton_stop_and_clean.clicked.connect(self.cleann_all)  # connect - для очистки всего
        self.pushButton_openDir.clicked.connect(self.open_folder_with_file)

    def init_convertermanager(self):
        os.environ['PATH'] += os.pathsep + os.path.abspath(Config.FFMPEG_PATH)
        self.thread_pool = QThreadPool()
        self.audibook_converter_signals = ConverterSignals()
        self.audibook_converter_signals.label_info_signal.connect(
            self.update_label)  # Подключаем вывод сообщений в label интерфейса
        self.audibook_converter_signals.label_info_signal_2.connect(
            self.update_label_2)  # Подключаем вывод сообщений в label 2 интерфейса
        self.audibook_converter_signals.all_tasks_completed.connect(
            self.on_all_tasks_completed)  # Подключаем сигнал завершения всех задач
        self.audibook_converter_signals.progress_bar_signal.connect(self.update_progress)

    def get_files(self):
        # print('get_files')  # Потом убрать!!!
        file_paths = []
        for i in range(self.newListWidget.count()):
            item = self.newListWidget.item(i)
            file_path = item.text()
            file_paths.append(file_path)
        return file_paths

    def open_folder_with_file(self):
        # Получаем путь к папке
        if folder_path := os.path.dirname(self.output_path):
            self.showMinimized()
            # Проверяем операционную систему
            if sys.platform == "win32":
                # Правильный формат пути для Windows
                normalized_path = os.path.normpath(self.output_path)
                subprocess.Popen(f'explorer /select,"{normalized_path}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", self.output_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])

    def get_metadata_widgets(self):
        return (
            self.lineEdit_title,
            self.lineEdit_artist,
            self.lineEdit_album,
            self.lineEdit_year,
            self.lineEdit_genre,
            self.lineEdit_albumartist,
            self.label_cover_of_book,
        )

    @staticmethod
    def update_audio_bitrate(bitrate):
        Config.set_audio_bitrate(bitrate)

    def add_files(self):
        self.file_manager.add_files(self.newListWidget)

    def remove_selected_files(self):
        self.file_manager.remove_files(self.newListWidget)
        # if self.file_manager.remove_files(self.newListWidget):
        #     self.metadata_manager.clear_metadata(*self.get_metadata_widgets())

    def cleann_all(self):
        self.newListWidget.clear()
        self.timer.reset_timer()
        self.metadata_manager.clear_metadata(*self.get_metadata_widgets())
        self.progressBar.setValue(0)
        self.update_label('Добавь файлы для создания новой книги')
        self.update_label_2('Или брось целиком папку в окно')
        self.tabWidget.setCurrentIndex(0)
        self.tableviewmanager.clean()

    def display_metadata(self):
        selected_items = self.newListWidget.selectedItems()
        if selected_items:
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
        cover_image_path = self.file_manager.upload_cover()
        self.metadata_manager.show_cover_image_path(cover_image_path)

    def checking_all_data(self):
        self.output_path = self.file_manager.get_output_file_path()
        self.audibook_converter_signals.label_info_signal_2.emit(f'{self.output_path}')
        if file_paths := self.get_files():
            self.file_paths = file_paths
        else:
            QMessageBox.warning(self, "Предупреждение", "Не выбраны файлы для аудиокниги")
            self.file_paths = []
        if self.output_path and self.file_paths:
            return True
        else:
            return False

    def start_conversion(self):
        if self.checking_all_data():
            self.timer.reset_timer()
            self.timer.start_timer()
            self.label_progress_description_2.clear()
            self.audibook_converter_signals.label_info_signal.emit('Запустил конвертацию..')

            bitrate = Config.AUDIO_BITRATE

            metadata = self.metadata_manager.metadata
            metadata['title'] = self.lineEdit_title.text()
            metadata['artist'] = self.lineEdit_artist.text()
            metadata['album'] = self.lineEdit_album.text()
            metadata['year'] = self.lineEdit_year.text()
            metadata['genre'] = self.lineEdit_genre.text()
            metadata['albumartist'] = self.lineEdit_albumartist.text()
            self.metadata = metadata

            self.completed_tasks = 0  # Сбрасываем счетчик выполненных задач
            self.progressBar.setValue(0)  # Сбрасываем прогрессбар
            self.quantity = len(self.file_paths)  # подсчитываем общее количество файлов
            self.output_temp_files_list = [None] * self.quantity  # Инициализируем список с None для каждого файла

            # Запускаем задачи
            for index, file in enumerate(self.file_paths):
                some_task = Converter(index=index, quantity=self.quantity, file=file,
                                      output_temp_files_list=self.output_temp_files_list, bitrate=bitrate)
                some_task.my_signals.progress_bar_signal.connect(self.update_progress)
                some_task.my_signals.label_info_signal.connect(self.update_label)
                some_task.my_signals.label_info_signal_2.connect(self.update_label_2)

                self.thread_pool.start(some_task)

            print('Все задачи запущены')  # Потом убрать!!!

    def update_label(self, value):
        max_length = 60
        shortened_text = value[:max_length] + '...' if len(value) > max_length else value
        self.label_progress_description.setText(shortened_text)

    def update_label_2(self, value):
        max_length = 90
        shortened_text = value[:max_length] + '...' if len(value) > max_length else value
        self.label_progress_description_2.setText(shortened_text)

    def update_progress(self):
        """Обновляет прогрессбар на основании выполнения задач."""
        self.completed_tasks += 1  # Увеличиваем количество завершённых задач
        progress_percentage = int((self.completed_tasks / self.quantity) * 100)  # Рассчитываем процент
        self.progressBar.setValue(progress_percentage)

        # Если все задачи завершены, отправляем сигнал
        if self.completed_tasks == self.quantity:
            self.audibook_converter_signals.all_tasks_completed.emit()

    def update_progress_2(self, value):
        self.progressBar.setValue(value)

    def on_all_tasks_completed(self):
        """Вызывается при завершении всех задач."""
        self.temp_files_list = [f.name for f in self.output_temp_files_list if f is not None]
        # print(temp_files_list)
        # QMessageBox.information(None, "Завершено", "Все задания выполнены!")
        self.audibook_converter_signals.label_info_signal.emit('Все файлы успешно конвертированы!')
        self.audibook_converter_signals.label_info_signal_2.emit('Запускаю объединение файлов..')

        # self.timer.stop_timer()
        # self.update_label('  ОСТАНОВКА!  ')
        # print('  ОСТАНОВКА!  ')
        # return

        m4bmerger = M4bMerger(self.temp_files_list, self.output_path, self.metadata)
        m4bmerger.my_signals.all_tasks_complete.connect(self.end_of_merge)
        m4bmerger.my_signals.progress_bar_signal.connect(self.update_progress)
        m4bmerger.my_signals.label_info_signal.connect(self.update_label)
        m4bmerger.my_signals.label_info_signal_2.connect(self.update_label_2)
        self.thread_pool.start(m4bmerger)

    def end_of_merge(self):
        self.delete_temp_files(self.temp_files_list)

    def delete_temp_files(self, temp_files_list):
        for temp_file in temp_files_list:
            if temp_file:
                os.remove(temp_file)  # Удаляем временные файлы
        self.audibook_converter_signals.label_info_signal.emit(f'Работа завершена, файл аудиокниги здесь:')
        self.audibook_converter_signals.label_info_signal_2.emit(f'{self.output_path}')
        self.progressBar.setValue(100)
        self.timer.stop_timer()

        # checkChapters(self.output_path)

        self.checkchapters.checkChapters(self.output_path)
        self.tabWidget.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AudiobookCreator()
    w.show()
    sys.exit(app.exec_())
