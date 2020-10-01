import re
import requests
import os

# utils:
# headers to send along with the request
def request_headers() -> dict:
    return {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

def clean_url(url: str) -> str:
    """
    'Cleans' the url
    """
    # ? Change "\u0026" to "&" and "\/" to "/"
    amp_pattern, fwd_slash_pattern = r"\\u0026", r"\\/"
    url = re.sub(amp_pattern, "&", url)
    url = re.sub(fwd_slash_pattern, "/", url)

    return url

file_count: int = 0
def create_file_name(video_title: str, path_to_save, is_video=True) -> str:
    """
    Creates a filename for video or audio accordingly

    Video filename suffix : .mp4
    Audio filename suffix: .mp3
    """
    global file_count

    filename_struct: str = "{}.mp3" if not is_video else "{}.mp4"
    tmp_filename: str = filename_struct.format(video_title)
    saved_filename: str = tmp_filename

    # if the same filename exists, append a number to distinguish
    for file in os.listdir(path_to_save):
        if os.path.isfile(file) and file == tmp_filename:
            video_title: str = video_title + "_#" + str(file_count)         
            saved_filename = filename_struct.format(video_title)
            file_count += 1
            break
    
    return saved_filename

def save_to_disk(response: requests.Response, video_title: str, path_to_save, is_video=True) -> None:
    """
    Saves to disk.
    
    @param is_video takes care of the filename
    """
    # check if the path exists
    # if not create, and download in it.
    if os.path.exists(path_to_save):
        os.chdir(path_to_save)
    else:
        print("This directory doesnot exist.")
        print("Creating and saving in this directory...")
        os.mkdir(path_to_save)
        os.chdir(path_to_save)

    # creates the filename and then starts saving to disk
    with open(create_file_name(video_title, path_to_save, is_video), "wb") as file_dl:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file_dl.write(chunk)

