import sys

from OpenGL.GL import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QOpenGLWidget


class MyGLWidget(QOpenGLWidget):
    def initializeGL(self):
        # Настройка начальных параметров OpenGL
        glClearColor(0.2, 0.3, 0.3, 1.0)

    def paintGL(self):
        # Отрисовка
        glClear(GL_COLOR_BUFFER_BIT)

        # Устанавливаем цвет для отрисовки треугольника
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex2f(0.0, 1.0)
        glColor3f(0.0, 1.0, 0.0)
        glVertex2f(-1.0, -1.0)
        glColor3f(0.0, 0.0, 1.0)
        glVertex2f(1.0, -1.0)
        glEnd()

    def resizeGL(self, w, h):
        # Подгоняем окно под размер
        glViewport(0, 0, w, h)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenGL Example")
        self.setGeometry(100, 100, 640, 480)

        # Используем QOpenGLWidget
        self.gl_widget = MyGLWidget(self)
        self.setCentralWidget(self.gl_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
