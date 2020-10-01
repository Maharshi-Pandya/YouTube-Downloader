import re
import json
import requests
import utils
import sys

from bs4 import BeautifulSoup

# Apna Karta Dharta
class YouTubeDownLoad:
    def __init__(self, video_url: str) -> None:
        self.video_url: str = video_url
        self._src_page_soup = self._create_soup()
        # dict containing info of the src urls
        self._final_json_dict: dict = self._create_json_dict()

        # the streaming formats for both audio and video
        self._video_streams, self._audio_streams = self._extract_streams()
        self._video_title: str = None

    # private:
    def _create_soup(self):
        print("\n::-> Fetching the video data")
        resp_page: requests.Response = requests.get(self.video_url, headers=utils.request_headers())
        return BeautifulSoup(resp_page.text, "html.parser")

    def _create_json_dict(self) -> dict:
        """
        Create the json dict for all the information regarding the video
        """
        pattern_to_strip: str = r";ytplayer\.web_player_context_config.+"

        # get the div which contains the target script
        ts_div = self._src_page_soup.find("div", id="player")

        target_script = str(
            ts_div.find("script", text=lambda txt: txt.startswith("var ytplayer"))
        )
        target_script = target_script.split(";", 1)[1]

        # strip the javascript from the script text
        tmp_json_str = target_script.split(" = ", 1)[1]
        tmp_json_str = re.sub(pattern_to_strip, "", tmp_json_str)

        tmp_json_dict: dict = json.loads(tmp_json_str)

        # the final json str which contains the info
        final_json_str: str = re.sub(
            r"\\\"", r"\"", tmp_json_dict["args"]["player_response"]
        )

        # uncomment if you wanna save the json to a file
        # with open("json_info.json", "w") as json_file:
        #     json_file.write(final_json_str)

        print("::-> Extracted video information")
        return json.loads(final_json_str)

    def _extract_streams(self) -> tuple:
        """
        Extract all the stream formats
        """
        video_streams, audio_streams = [], []

        # first append to video streams from the "formats" key
        for stream_index in range(
            len(self._final_json_dict["streamingData"]["formats"])
        ):
            stream_dict: dict = {}
            stream: dict = self._final_json_dict["streamingData"]["formats"][stream_index]

            try:
                stream_dict["src_url"] = stream["url"]
                stream_dict["bitrate"] = stream["bitrate"]
                stream_dict["mime_type"] = stream["mimeType"]
                stream_dict["quality_label"] = stream["qualityLabel"]
                video_streams.append(stream_dict)
            except:
                print("::-> Detected signature ciphers in the video data")
                print("Error: Unable to start the download\n")
                sys.exit()

        # ik ik.....but will refactor it later

        for stream_index in range(
            len(self._final_json_dict["streamingData"]["adaptiveFormats"])
        ):
            stream_dict: dict = {}
            stream: dict = self._final_json_dict["streamingData"]["adaptiveFormats"][
                stream_index
            ]

            stream_dict["src_url"] = stream["url"]
            stream_dict["bitrate"] = stream["bitrate"]
            stream_dict["mime_type"] = stream["mimeType"]

            try:
                stream_dict["quality_label"] = stream["qualityLabel"]
            except KeyError:
                pass

            # if mimeType is a "video", append to video stream
            if stream_dict["mime_type"].startswith("video"):
                video_streams.append(stream_dict)
            else:
                audio_streams.append(stream_dict)

        return (video_streams, audio_streams)

    # public:
    def get_audio_streams(self) -> list:
        """
        Get all the streaming formats of the audio only
        """
        return self._audio_streams

    def get_video_streams(self) -> list:
        """
        Get all the streaming formats of the video (audio may/maynot be included)
        """
        return self._video_streams

    def get_all_streams(self) -> list:
        """
        Get all the streaming formats of both, the video and its audio, with src urls
        """
        all_streams = []
        total_len = len(self._video_streams) + len(self._audio_streams)
        for idx in range(total_len):
            if idx >= len(self._video_streams):
                all_streams.append(self._audio_streams[idx - len(self._video_streams)])
            else:
                all_streams.append(self._video_streams[idx])
        return all_streams

    def get_video_title(self) -> str:
        self._video_title = self._final_json_dict["videoDetails"]["title"]
        return self._video_title

    def download(self, vid_format: str) -> None:
        """
        Downloads the video.
        Current resolutions supported: 360p and 720p
        """
        if vid_format == "360p" or vid_format == "720p":
            vid_src_url = None
            for idx in range(len(self._video_streams)):
                if self._video_streams[idx]["quality_label"] == vid_format:
                    vid_src_url = self._video_streams[idx]["src_url"]
                    break

            # got the source url
            vid_src_url = utils.clean_url(vid_src_url)

            print("::-> Download in progress...")
            # get the response from the src url in chunks (stream=True)
            response = requests.get(vid_src_url, headers=utils.request_headers(), stream=True)
            response.raise_for_status()

            utils.save_to_disk(response, self.get_video_title(), is_video=True)

        else:
            print("The only supported formats for downloading a video is 360p and 720p for now!")

    def download_audio(self, path_to_save=None) -> None:
        """
        Downloads only the audio from the video. 
        Format: .mp3

        (Useful when downloading songs from YouTube)
        """
        audio_src_url = self._audio_streams[0]["src_url"]    # download the first one from the audio streams

        # clean the url first
        audio_src_url = utils.clean_url(audio_src_url)

        print("::->Download in progress...")
        # request the audio source
        audio_resp = requests.get(audio_src_url, headers=utils.request_headers(), stream=True)
        audio_resp.raise_for_status()

        # save to disk with is_video not set
        utils.save_to_disk(audio_resp, self.get_video_title(), path_to_save, is_video=False)
