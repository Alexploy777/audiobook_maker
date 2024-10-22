import sys
from PyQt5.QtWidgets import *

from gui import Ui_MainWindow
from custom_list_widget import CustomListWidget  # Новый класс


class MyAplication(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyAplication, self).__init__()
        self.ui = Ui_MainWindow()
        self.setupUi(self)
        self.setWindowTitle('')

        # Заменяем стандартный listWidget на кастомный CustomListWidget
        self.newListWidget = CustomListWidget(self)

        # Устанавливаем его на место старого listWidget
        self.verticalLayout.replaceWidget(self.ui.listWidget, self.newListWidget)
        self.listWidget.deleteLater()  # Удаляем старый виджет


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyAplication()
    w.show()
    sys.exit(app.exec_())
