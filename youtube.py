import re
import os
from pytube import YouTube

# all files will be downloaded in that file
path = r'C:\Users\dimartart\Desktop'


# validation of youtube link
def is_youtube_url(url: str) -> bool:
    regex = re.compile(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*")
    results = regex.search(url)
    if not results:
        return False

    return True


# we check if video/audio from youtube is higher than 50 megabyte
def is_lower_than_50mb(url: str, file_type: str) -> bool:
    yt = YouTube(url)
    stream = yt.streams.get_audio_only() if file_type == "audio" else yt.streams.get_highest_resolution()
    return stream.filesize_mb < 50


def delete_file(path_to_file: str) -> None:
    try:
        os.remove(path_to_file)
    except Exception as e:
        print("error during deleting the file", str(e))


# main func for downloading video or audio from youtube
def download_file(url: str, file_type: str) -> str:
    try:
        yt = YouTube(url)
        if file_type == "video":
            file = yt.streams.get_highest_resolution()
        else:
            file = yt.streams.get_audio_only()

        path_to_file = file.download(path)

        return path_to_file

    except Exception as e:
        print("error during downloading the file", str(e))


if __name__ == '__main__':
    pass



