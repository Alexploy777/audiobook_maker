import subprocess
import json

from gui import TableViewManager


# from mutagen.mp4 import MP4
# from gui import CustomListWidget

class CheckChapters:
    def __init__(self, output_witget):
        # self.tableviewmanager = TableViewManager(output_witget, ['Имя главы', 'Время начала'])
        self.output_witget = output_witget

    def checkChapters(self, file_path):
        # Команда ffprobe для получения информации о главах в формате JSON
        result = subprocess.run(
            ["ffprobe", "-i", file_path, "-print_format", "json", "-show_chapters", "-loglevel", "error"],
            capture_output=True,
            text=True, creationflags=subprocess.CREATE_NO_WINDOW, encoding='utf-8'  # Указываем кодировку для вывода
        )

        # Проверяем результат выполнения
        if result.returncode != 0:
            print("Ошибка при выполнении ffprobe:", result.stderr)  # Потом убрать!!!
            return []

        try:
            # Парсим вывод как JSON
            chapters_data = json.loads(result.stdout)
            chapters = []

            # Извлекаем список глав
            for chapter in chapters_data.get("chapters", []):
                start_time = float(chapter["start_time"])
                title = chapter["tags"].get("title", f"Chapter {len(chapters) + 1}")
                chapters.append((title, start_time))

            self.output_witget.add_row_list(['', ''])

            for i, (title, start_time) in enumerate(chapters, 1):
                print(f"Глава {i}: {title} - старт с {self.format_time(start_time)} сек.")
                self.output_witget.add_row_list([f'  {title}', f'    {self.format_time(start_time)} сек.'])
                # newListWidget.show_in_newListWidget(f"Глава {i}: {title} - старт с {format_time(start_time)} сек.")

            # return chapters

        except json.JSONDecodeError:
            print("Ошибка при разборе JSON данных.")
            return []

    def format_time(self, seconds):
        # Преобразование секунд в формат чч:мм:сс
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hrs:02}:{mins:02}:{secs:05.2f}"


if __name__ == '__main__':
    pass
