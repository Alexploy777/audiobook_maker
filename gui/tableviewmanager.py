from PyQt5.QtWidgets import QTableView, QMainWindow
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class TableViewManager:
    def __init__(self, table_view: QTableView, headers: list):
        """
        Класс для управления выводом данных в QTableView.

        :param table_view: Виджет QTableView, в который выводятся данные.
        :param headers: Список заголовков для колонок таблицы.
        """
        self.table_view = table_view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(headers)
        self.table_view.setModel(self.model)

        # Отключаем индексы строк
        self.table_view.verticalHeader().setVisible(False)

    def add_row_list(self, values: list):
        """
        Добавляет новую строку в таблицу.

        :param values: Список значений, которые будут добавлены в новую строку.
        """
        row = [QStandardItem(str(value)) for value in values]
        self.model.appendRow(row)

        # Подстраиваем ширину колонок под содержимое
        self.table_view.resizeColumnsToContents()

        # Добавляем немного ширины каждой колонке (например, +20 пикселей)
        extra_width = 20
        for column in range(self.model.columnCount()):
            current_width = self.table_view.columnWidth(column)
            self.table_view.setColumnWidth(column, current_width + extra_width)

    def clean(self):
        """
        Очищает все строки в таблице.
        """
        self.model.removeRows(0, self.model.rowCount())


if __name__ == '__main__':
    pass
