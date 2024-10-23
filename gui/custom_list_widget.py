import os
from PyQt5.QtWidgets import QListWidget, QAbstractItemView
from PyQt5.QtCore import Qt


class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)  # Включаем внутреннее перемещение элементов
        self.setDefaultDropAction(Qt.MoveAction)  # Устанавливаем действие перемещения по умолчанию
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.allowed_extensions = allowed_extensions

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.source() == self:
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.source() == self:
            super(CustomListWidget, self).dropEvent(event)  # Внутреннее перемещение
        else:
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                file_path = os.path.normpath(file_path)  # Нормализуем путь
                if os.path.isdir(file_path):  # Если это папка
                    self._add_files_from_folder(file_path)
                else:
                    if file_path.endswith(self.allowed_extensions):  # Если это файл с нужным расширением
                        self.addItem(file_path)
            self.setCurrentRow(0)


    def _add_files_from_folder(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(self.allowed_extensions):
                    full_path = os.path.normpath(os.path.join(root, file))  # Нормализуем путь к файлу
                    self.addItem(full_path)
