import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QAbstractItemView
from PyQt5.QtCore import Qt


class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super(FileListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)  # Включаем внутреннее перемещение элементов
        self.setDefaultDropAction(Qt.MoveAction)  # Устанавливаем действие перемещения по умолчанию
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.source() == self:
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.source() == self:
            super(FileListWidget, self).dropEvent(event)  # Внутреннее перемещение
        else:
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                file_path = os.path.normpath(file_path)  # Нормализуем путь
                if os.path.isdir(file_path):  # Если это папка
                    self._add_files_from_folder(file_path)
                else:
                    if file_path.endswith(('.mp3', '.m4a')):  # Если это файл с нужным расширением
                        self.addItem(file_path)

    def _add_files_from_folder(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.mp3', '.m4a')):
                    full_path = os.path.normpath(os.path.join(root, file))  # Нормализуем путь к файлу
                    self.addItem(full_path)


class FileDropApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.listWidget = FileListWidget()

        self.button = QPushButton('Открыть файлы')
        self.button.clicked.connect(self.open_files)

        layout.addWidget(self.listWidget)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setWindowTitle('Файловый менеджер')
        self.setGeometry(300, 300, 400, 300)

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы", "", "Audio Files (*.mp3 *.m4a)")
        if files:
            # Нормализуем пути перед добавлением в список
            normalized_files = [os.path.normpath(file) for file in files]
            self.listWidget.addItems(normalized_files)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileDropApp()
    ex.show()
    sys.exit(app.exec_())
