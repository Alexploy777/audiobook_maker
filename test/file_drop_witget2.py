import sys
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt

import sys
from PyQt5.QtWidgets import *

from untitled import Ui_MainWindow


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWidget, self).__init__()
        self.ui = Ui_MainWindow()
        self.setupUi(self)
        self.setWindowTitle('dsdfgdfg')

        self.listWidget = QListWidget()
        self.listWidget.setAcceptDrops(True)
        self.listWidget.dropEvent = self.drop_event

        # ... остальной интерфейс

    def drop_event(self, event):
        print('drop event')
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                item = QListWidgetItem(file_path)
                self.listWidget.addItem(item)
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWidget()
    w.show()
    sys.exit(app.exec_())
