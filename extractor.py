# This class extracts all the necessary information about the
# YouTube video useful for downloading

import requests
import utils
from bs4 import BeautifulSoup


class Extractor:
    def __init__(self, yt_vid_url):
        self.video_url = yt_vid_url
        self._src_page_soup = None
        self._final_json_dict = None

    # private:
    def _create_soup(self):
        print("\n::-> Fetching the video data")
        try:
            resp_page: requests.Response = requests.get(
                self.video_url, headers=utils.request_headers()
            )
            soup = BeautifulSoup(resp_page.text, "html.parser")
        except:
            print("::-> Something went wrong while trying to scrape the video data\n")
            print("Here's the error stack!!!\n")
            raise

        self._src_page_soup = soup
