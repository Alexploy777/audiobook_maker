import os
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor

os.environ['PATH'] += os.pathsep + os.path.abspath('external')


class Converter:
    def __init__(self, output_dir_name):
        self.output_dir_name = output_dir_name

    def get_output_file_path(self, input_path):
        temp = os.path.abspath(input_path)
        dir_name = os.path.dirname(os.path.dirname(temp))
        full_output_dir = os.path.join(dir_name, self.output_dir_name)
        os.makedirs(full_output_dir, exist_ok=True)
        name = os.path.basename(temp).split(os.extsep)[0]
        output_name = os.path.join(str(full_output_dir), name + '.m4b')
        return output_name

    def convert_mp3_to_m4b(self, input_path):
        audio = AudioSegment.from_mp3(input_path)
        output_full_path = self.get_output_file_path(input_path)
        audio.export(output_full_path, format="mp4", codec="aac")
        print(f"Файл успешно конвертирован: {output_full_path}")

    def start(self, input_list):
        with ThreadPoolExecutor() as executor:
            executor.map(self.convert_mp3_to_m4b, input_list)


if __name__ == '__main__':
    input_list = ['mp3/1.mp3', 'mp3/2.mp3', 'mp3/3.mp3', 'mp3/4.mp3']
    output_dir_name = 'mp4'
    converter = Converter(output_dir_name)
    converter.start(input_list)
