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

    def dropEvent(self, event):
        print('dragdroplistwidget')
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                self.addItem(url.toLocalFile())
            event.acceptProposedAction()
        else:
            event.ignore()
