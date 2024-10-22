# data/file_manager.py
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QListWidget


class FileManager:
    def __init__(self, audiobookcreator):
        self.lineEdit_title = audiobookcreator.lineEdit_title
        self.lineEdit_artist = audiobookcreator.lineEdit_artist
        self.file_paths = []
        self.cover_image_path = None

    def add_files(self, listwidget: QListWidget) -> None:
        """
            Добавляет выбранные MP3 файлы из выбранной папки в список.

            Args:
                listwidget: QListWidget, в который будут добавлены пути к файлам.
        """
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Выберите MP3 файлы", "", "MP3 Files (*.mp3);;All Files (*)",
                                                     options=options)

        if file_paths:
            for path in file_paths:
                if path not in self.file_paths:
                    self.file_paths.append(path)
                    listwidget.addItem(path)
                else:
                    QMessageBox.warning(None, "Предупреждение", f"Файл {path} уже добавлен.")
            if listwidget.count() > 0:
                listwidget.setCurrentRow(0)  # Выделяется первый элемент списка

    def remove_files(self, listwidget):
        selected_items = listwidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(None, "Предупреждение", "Нет выбранных файлов для удаления.")
        else:
            for item in selected_items:
                file_path = item.text()
                if file_path in self.file_paths:
                    self.file_paths.remove(file_path)
                listwidget.takeItem(listwidget.row(item))

    @staticmethod
    def upload_cover():
        options = QFileDialog.Options()
        cover_image_path, _ = QFileDialog.getOpenFileName(None, "Выберите изображение обложки", "",
                                                          "Images (*.png *.jpg *.bmp);;All Files (*)", options=options)
        if cover_image_path:
            return cover_image_path
        else:
            QMessageBox.warning(None, "Предупреждение", "Изображение не выбрано.")

    def get_output_file_path(self):
        name = self.lineEdit_artist.text() + '-' + self.lineEdit_title.text()
        options = QFileDialog.Options()
        output_file_path, _ = QFileDialog.getSaveFileName(None, "Выберите куда сохранить аудиокнигу", name,
                                                          "M4B Files (*.m4b);;All Files (*)", options=options)
        if output_file_path:
            return output_file_path
        else:
            QMessageBox.warning(None, "Предупреждение", "Не выбран путь для сохранения файла.")
            return None
