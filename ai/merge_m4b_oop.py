import subprocess
import os


class M4BMerger:
    def __init__(self, input_files, output_file):
        self.input_files = input_files  # Список m4b файлов
        self.output_file = output_file  # Финальный выходной файл
        self.list_file = 'files.txt'  # Временный файл со списком входных файлов

    def create_file_list(self):
        """Создаем временный файл со списком входных m4b файлов."""
        with open(self.list_file, 'w') as f:
            for file in self.input_files:
                f.write(f"file '{file}'\n")

    def merge_files(self):
        """Объединяем m4b файлы с помощью ffmpeg."""
        command = [
            'ffmpeg',
            '-f', 'concat',  # формат ввода: список файлов
            '-safe', '0',  # разрешаем использовать небезопасные символы в путях
            '-i', self.list_file,  # вводим файл со списком
            '-c', 'copy',  # копируем содержимое без перекодирования
            '-y',  # перезаписываем выходной файл без предупреждения
            self.output_file  # выходной файл
        ]

        try:
            # Запускаем процесс ffmpeg
            subprocess.run(command, check=True)
            print(f'Файлы успешно объединены в {self.output_file}')
        except subprocess.CalledProcessError as e:
            print(f'Ошибка при объединении файлов: {e}')

    def clean_up(self):
        """Удаляем временные файлы."""
        if os.path.exists(self.list_file):
            os.remove(self.list_file)

    def run(self):
        """Основной метод для выполнения всех шагов."""
        self.create_file_list()
        self.merge_files()
        self.clean_up()

if __name__ == '__main__':
    # Пример использования
    input_files = [
        r'temp\1.m4b',
        r'temp\2.m4b',
        r'temp\3.m4b',
        r'temp\4.m4b'
    ]

    output_file = r'final.m4b'

    merger = M4BMerger(input_files, output_file)
    merger.run()
