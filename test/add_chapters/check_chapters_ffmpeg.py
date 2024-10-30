import os
import subprocess

os.environ['PATH'] += os.pathsep + os.path.abspath('external')

import json


def extract_chapters_with_ffprobe(file_path):
    # Команда ffprobe для получения информации о главах в формате JSON
    result = subprocess.run(
        ["ffprobe", "-i", file_path, "-print_format", "json", "-show_chapters", "-loglevel", "error"],
        capture_output=True,
        text=True,
        encoding='utf-8'  # Указываем кодировку для вывода
    )

    # Проверяем результат выполнения
    if result.returncode != 0:
        print("Ошибка при выполнении ffprobe:", result.stderr)
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

        return chapters

    except json.JSONDecodeError:
        print("Ошибка при разборе JSON данных.")
        return []


def format_time(seconds):
    # Преобразование секунд в формат чч:мм:сс
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:05.2f}"


if __name__ == '__main__':
    # Пример использования
    file_path = "your_audio_file.m4b"
    chapters = extract_chapters_with_ffprobe(file_path)
    for i, (title, start_time) in enumerate(chapters, 1):
        print(f"Глава {i}: {title} - старт с {format_time(start_time)} сек.")
