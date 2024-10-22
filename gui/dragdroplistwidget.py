import os

from PyQt5.QtWidgets import QListWidget


class DragDropListWidget(QListWidget):
    def __init__(self, files):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            print("Urls detected")
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    # def dropEvent(self, event):
    #     print('dragdroplistwidget')
    #     if event.mimeData().hasUrls():
    #         for url in event.mimeData().urls():
    #             self.addItem(url.toLocalFile())
    #         event.acceptProposedAction()
    #     else:
    #         event.ignore()

    def dropEvent(self, event):
        print('dropEvent')
        # Получаем список файлов из события
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            print(file_path)
            if os.path.isfile(file_path) and file_path.lower().endswith('.mp3'):
                # Добавляем файл в QListWidget
                self.addItem(os.path.abspath(file_path))
            elif os.path.isdir(file_path):
                for root, _, files in os.walk(file_path):
                    print(root, _, files)
                    for file in files:
                        if file.lower().endswith('.mp3'):
                            self.addItem(os.path.abspath(root + '/' + file))
