from PyQt5.QtWidgets import QTabWidget


def replace_widget(parent, old_widget, new_widget):
    # Проверяем, есть ли у `old_widget` родительский компоновщик
    layout = old_widget.parentWidget().layout()
    if layout is None:
        raise ValueError("Cannot replace widget - parent layout not found.")

    # Находим индекс `old_widget` в компоновке
    index = layout.indexOf(old_widget)
    if index == -1:
        raise ValueError("Old widget not found in the layout.")

    # Получаем позицию и настройки `old_widget` в компоновке
    item = layout.takeAt(index)

    # Удаляем `old_widget` из родительского компоновщика
    old_widget.setParent(None)

    # Заменяем `old_widget` на `new_widget` в той же позиции
    layout.insertWidget(index, new_widget)

    # Пример для QTabWidget: Если `old_widget` находится в QTabWidget, обрабатываем его отдельно
    if isinstance(parent, QTabWidget):
        tab_index = parent.indexOf(old_widget)
        if tab_index != -1:
            parent.removeTab(tab_index)
            parent.insertTab(tab_index, new_widget, new_widget.windowTitle())  # Можно указать заголовок вкладки
