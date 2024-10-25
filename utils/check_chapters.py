from mutagen.mp4 import MP4


def checkChapters(output_file):
    audio = MP4(output_file)
    if 'chpl' in audio:
        chapters = audio['chpl']
        for idx, chapter in enumerate(chapters, 1):
            start_time, title = chapter['start_time'], chapter['title']
            print(f"Глава {idx}: начало {start_time / 1000} сек., заголовок: {title}")
    else:
        print("Главы не найдены в файле.")
