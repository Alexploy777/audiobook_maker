import sys
import os
from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QVBoxLayout, QWidget


class FileDropWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag and Drop MP3 Files")

        # Создаем QPlainTextEdit
        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setAcceptDrops(True)  # Разрешаем перетаскивание

        # Устанавливаем макет
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        # Явное назначение метода dropEvent
        self.text_edit.dropEvent = self.dropEvent

    def dragEnterEvent(self, event):
        print('dragEnterEvent')
        # Проверяем, являются ли данные перетаскиваемыми файлами
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()  # Игнорируем событие, если оно не содержит URL

    def dropEvent(self, event):
        print("Drop event triggered")  # Отладочное сообщение
        # Получаем список файлов из события
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()  # Получаем локальный путь
            print(f"Dropped: {file_path}")  # Отладочное сообщение
            if os.path.isfile(file_path) and file_path.lower().endswith('.mp3'):
                # Добавляем файл в QPlainTextEdit без префикса
                self.text_edit.appendPlainText(file_path)
            elif os.path.isdir(file_path):
                # Если это папка, добавляем все mp3 файлы из нее
                for root, _, files in os.walk(file_path):
                    for file in files:
                        if file.lower().endswith('.mp3'):
                            full_path = os.path.join(root, file)  # Полный путь к файлу
                            self.text_edit.appendPlainText(full_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileDropWidget()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())
