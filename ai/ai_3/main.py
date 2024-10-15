import sys
from PyQt5.QtWidgets import *

from ai.ai_3.audio_processing_new import ConverterManager
from gui import Ui_MainWindow


class ProgressBarGui(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ProgressBarGui, self).__init__()
        self.ui = Ui_MainWindow()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.start)

    def start(self):
        converter_manager = ConverterManager(self.progressBar)
        converter_manager.start(input_list=input_list)
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ProgressBarGui()
    w.show()
    sys.exit(app.exec_())