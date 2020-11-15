import re
import random
import requests
import os

# utils:
# headers to send along with the request
def request_headers() -> dict:
    # user agents
    usr_agent_str: list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    ]
    # select random
    rand_usr_agent_str: str = random.choice(usr_agent_str)
    headers: dict = {"User-Agent": rand_usr_agent_str}
    return headers


def sanitize_url(url: str) -> str:
    """
    'Cleans' the url
    """
    # ? Change "\u0026" to "&" and "\/" to "/"
    amp_pattern, fwd_slash_pattern = r"\\u0026", r"\\/"
    url = re.sub(amp_pattern, "&", url)
    url = re.sub(fwd_slash_pattern, "/", url)

    return url


file_count: int = 0  # counter for num of files


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


def save_to_disk(
    response: requests.Response, video_title: str, path_to_save, is_video=True
) -> None:
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

    # patterns for slashes
    slash_patt = [
        r"\/+",
        r"\\+",
    ]
    # when the video title contains "/+" or "\+" change it to "_"
    for patt in slash_patt:
        if re.search(patt, video_title):
            video_title = re.sub(patt, "_", video_title)

    # creates the filename and then starts saving to disk
    with open(create_file_name(video_title, path_to_save, is_video), "wb") as file_dl:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file_dl.write(chunk)

