from PyQt5.QtWidgets import QTabWidget


class WidgetReplacer:
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget

    def replace_widget(self, old_widget, new_widget):
        """
        Метод для замены old_widget на new_widget внутри parent_widget.
        """
        # Находим компоновку родителя
        layout = old_widget.parentWidget().layout()
        if layout is None:
            raise ValueError("Cannot replace widget - parent layout not found.")

        # Находим индекс виджета
        index = layout.indexOf(old_widget)
        if index == -1:
            raise ValueError("Old widget not found in the layout.")

        # Удаляем старый виджет и вставляем новый
        layout.takeAt(index)
        old_widget.setParent(None)
        layout.insertWidget(index, new_widget)

        # Дополнительная проверка для QTabWidget
        if isinstance(self.parent_widget, QTabWidget):
            tab_index = self.parent_widget.indexOf(old_widget)
            if tab_index != -1:
                self.parent_widget.removeTab(tab_index)
                self.parent_widget.insertTab(tab_index, new_widget, new_widget.windowTitle())

        # Возвращаем ссылку на новый виджет
        return new_widget

    def replace_widget_in_tab(self, tab_widget, old_widget, new_widget):
        """
        Метод для замены виджета, если он находится внутри QTabWidget.
        """
        tab_index = tab_widget.indexOf(old_widget)
        if tab_index != -1:
            tab_widget.removeTab(tab_index)
            tab_widget.insertTab(tab_index, new_widget, new_widget.windowTitle())
        else:
            raise ValueError("Old widget not found in QTabWidget.")

        return new_widget

# def replace_widget(parent, old_widget, new_widget):
#     # Проверяем, есть ли у `old_widget` родительский компоновщик
#     layout = old_widget.parentWidget().layout()
#     if layout is None:
#         raise ValueError("Cannot replace widget - parent layout not found.")
#
#     # Находим индекс `old_widget` в компоновке
#     index = layout.indexOf(old_widget)
#     if index == -1:
#         raise ValueError("Old widget not found in the layout.")
#
#     # Получаем позицию и настройки `old_widget` в компоновке
#     item = layout.takeAt(index)
#
#     # Удаляем `old_widget` из родительского компоновщика
#     old_widget.setParent(None)
#
#     # Заменяем `old_widget` на `new_widget` в той же позиции
#     layout.insertWidget(index, new_widget)
#
#     # Пример для QTabWidget: Если `old_widget` находится в QTabWidget, обрабатываем его отдельно
#     if isinstance(parent, QTabWidget):
#         tab_index = parent.indexOf(old_widget)
#         if tab_index != -1:
#             parent.removeTab(tab_index)
#             parent.insertTab(tab_index, new_widget, new_widget.windowTitle())  # Можно указать заголовок вкладки
