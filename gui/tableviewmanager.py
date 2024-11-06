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

    def add_row(self, values: list):
        """
        Добавляет новую строку в таблицу.

        :param values: Список значений, которые будут добавлены в новую строку.
        """
        row = [QStandardItem(str(value)) for value in values]
        self.model.appendRow(row)

    def clean(self):
        """
        Очищает все строки в таблице.
        """
        self.model.removeRows(0, self.model.rowCount())


if __name__ == '__main__':
    pass
