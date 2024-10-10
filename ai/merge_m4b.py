import subprocess
import os


def merge_m4b_files(input_files, output_file):
    # Создаем временный файл со списком всех входных файлов
    list_file = 'files.txt'

    # Открываем файл и записываем пути к файлам
    with open(list_file, 'w') as f:
        for file in input_files:
            # ffmpeg требует, чтобы пути к файлам были в формате 'file path'
            f.write(f"file '{file}'\n")

    # Команда для объединения файлов с помощью ffmpeg
    command = [
        'ffmpeg',
        '-f', 'concat',  # формат ввода: список файлов
        '-safe', '0',  # разрешаем использовать небезопасные символы в путях
        '-i', list_file,  # вводим файл со списком
        '-c', 'copy',  # копируем содержимое без перекодирования
        output_file  # выходной файл
    ]

    try:
        # Запускаем процесс ffmpeg
        subprocess.run(command, check=True)
        print(f'Файлы успешно объединены в {output_file}')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка при объединении файлов: {e}')
    finally:
        # Удаляем временный файл со списком
        if os.path.exists(list_file):
            os.remove(list_file)

if __name__ == '__main__':
    # Пример использования
    input_files = [
        r'D:\1.m4b',
        r'D:\2.m4b',
        r'D:\3.m4b',
        r'D:\4.m4b'
    ]

    output_file = r'D:\final2.m4b'

    merge_m4b_files(input_files, output_file)
