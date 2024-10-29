from mutagen.mp4 import MP4


class MergeAndChapters:
    def __init__(self, input_files_list, output_file):
        self.input_files_list = input_files_list
        self.output_file = output_file

    def merge(self):
        pass

    def add_chapters(self):
        pass

    def checkChapters(self):
        audio = MP4(self.output_file)
        if 'chpl' in audio:
            chapters = audio['chpl']
            for idx, chapter in enumerate(chapters, 1):
                start_time, title = chapter['start_time'], chapter['title']
                print(f"Глава {idx}: начало {start_time / 1000} сек., заголовок: {title}")
        else:
            print("Главы не найдены в файле.")


if __name__ == '__main__':
    input_files_list = ['1.m4b', '2.m4b', '3.m4b']
    output_file = 'output.m4b'
