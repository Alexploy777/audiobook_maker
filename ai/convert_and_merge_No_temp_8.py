import subprocess

class Merger:
    def __init__(self, input_files, output_file):
        self.input_files = input_files  # Список временных файлов
        self.output_file = output_file  # Выходной файл

    def merge_files(self):
        ffmpeg_command = [
            'ffmpeg',
            '-i', '-',  # stdin как вход
            '-c', 'copy',  # Без перекодирования
            '-y',  # Перезапись выходного файла
            self.output_file  # Имя выходного файла
        ]

        # Создаем процесс ffmpeg с вводом через stdin
        with subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE) as process:
            for file_data in self.input_files:
                file_data.seek(0)  # Убедитесь, что указатель файла находится в начале
                process.stdin.write(file_data.read())  # Чтение данных из файла и передача их в stdin
            process.stdin.close()  # Закрываем stdin после записи всех данных
            process.wait()  # Ожидаем завершения процесса ffmpeg

    def run(self):
        """Основной метод для выполнения всех шагов."""
        self.merge_files()

class ConverterManager:
    def __init__(self, input_files, output_file):
        self.input_files = input_files
        self.output_file = output_file

    def start(self):
        merger = Merger(self.input_files, self.output_file)
        merger.run()

if __name__ == '__main__':
    input_list = [open('mp3/4.mp3', 'rb'), open('mp3/1.mp3', 'rb'), open('mp3/3.mp3', 'rb'), open('mp3/2.mp3', 'rb')]
    output_file = 'final.m4b'
    converter_manager = ConverterManager(input_list, output_file)
    converter_manager.start()

    # Закрываем все временные файлы после использования
    for file in input_list:
        file.close()
