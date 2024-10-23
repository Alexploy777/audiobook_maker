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

        # Удаляем старый listWidget из компоновки
        self.verticalLayout.removeWidget(self.listWidget)
        self.listWidget.deleteLater()  # Удаляем стандартный listWidget

        # Создаем кастомный CustomListWidget
        self.newListWidget = CustomListWidget(self.groupBox_files)

        # Добавляем новый виджет в компоновку на место старого
        self.verticalLayout.addWidget(self.newListWidget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyAplication()
    w.show()
    sys.exit(app.exec_())
