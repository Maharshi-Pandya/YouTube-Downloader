import os
import re
import sys
import glob
import json

import requests

from bs4 import BeautifulSoup


# utils for this class
import utils

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
        try:
            resp_page: requests.Response = requests.get(self.video_url, headers=utils.request_headers())
            soup = BeautifulSoup(resp_page.text, "html.parser")
        except:
            print("::-> Something went wrong while trying to scrape the video data\n")
            print("Here's the error stack!!!\n")
            raise

        return soup

    def _create_json_dict(self) -> dict:
        """
        Create the json dict for all the information regarding the video
        """
        pattern_to_strip: str = r";ytplayer\.web_player_context_config.+"

        try:
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
            # json_file.write(final_json_str)

            print("::-> Extracted video information")
            return json.loads(final_json_str)

        except:
            print("Error: Invalid/Incorrect/Incomplete input provided\n")
            sys.exit()


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

        # ik ik.....but will refactor it later (i wont)
        
        # Essentially the json dict has two keys,
        # "formats" and "adaptiveFormats" 
        # "formats" key have video source URLs with audio in them
        # "adaptiveFormats" key have both the video (w/o audio) and audio source URLs, but seperated.
        # This key has 144p to 1080p quality included, whereas "formats" key have either 360p 
        # or 720p quality in it.

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
                # this means it is an audio stream
                stream_dict["audio_quality"] = stream["audioQuality"]

            # if mimeType is a "video", append to video stream
            if stream_dict["mime_type"].startswith("video"):
                video_streams.append(stream_dict)
            else:
                audio_streams.append(stream_dict)

        return (video_streams, audio_streams)

    def _download_video(self, vid_url: str, path_to_save=None) -> None:
        try:
            vid_resp = requests.get(vid_url, headers=utils.request_headers(), stream=True)
            vid_resp.raise_for_status()
        except:
            print("::-> An error occurred while requesting the file")
            raise

        # save the video file
        utils.save_to_disk(vid_resp, self.get_video_title(), path_to_save, is_video=True)
        print("Done!\n")

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

    def download(self, vid_format: str, path_to_save=None) -> None:
        """
        Downloads the video.
        Current resolutions supported: all
        """
        if not vid_format:
            print("Error: quality/resolution must not be None")

        vid_src_url: str = None
        vid_wa_url: str = None  # video without audio url
        for stream in self._video_streams:
            if stream["quality_label"] == vid_format: 
                if re.search(",", stream["mime_type"]):
                    vid_src_url: str = stream["src_url"]
                    break
                else:
                    vid_wa_url: str = stream["src_url"]
                    break


        if vid_src_url:
            # got the source url
            vid_src_url: str = utils.sanitize_url(vid_src_url)

            print("::-> Download in progress...")
            # ? get the response from the src url in chunks (stream=True)
            try:
                response: requests.Response = requests.get(vid_src_url, headers=utils.request_headers(), stream=True)
                response.raise_for_status()
            except:
                print("::-> An error occurred while requesting the file.")
                raise

            utils.save_to_disk(response, self.get_video_title(), path_to_save, is_video=True)

            # endif

        # ? When the video and audio urls are different
        elif vid_wa_url:
        # clean the url
            vid_wa_url: str = utils.sanitize_url(vid_wa_url)

            # download audio and video files to be combined
            self.download_audio(path_to_save)
            print("::-> Downloading the video file...")
            self._download_video(vid_wa_url, path_to_save)

            # get to know which video and audio files needs to be combined
            if path_to_save[len(path_to_save) - 1] != "/":
                path_to_save += "/"

            vid_filelist: list = glob.glob(path_to_save + "*.mp4")
            last_vid_file: str = max(vid_filelist, key=os.path.getctime)
            audio_filelist: list = glob.glob(path_to_save + "*.mp3")
            last_audio_file: str = max(audio_filelist, key=os.path.getctime)

            # use ffmpeg to combine both, audio and video
            print("::-> Combining the audio and video files into one video file...")

            # redirect all stdout and stderr to /dev/null
            # keep the console clean
            cmd: str = f"ffmpeg -v quiet -i \"{last_vid_file}\" -i \"{last_audio_file}\" -map 0:v:0 -map 1:a:0 \"{self.get_video_title()}_final.mp4\" > /dev/null 2>&1"
            # finally execute the command
            ffmpeg_exitcode = os.system(cmd)

            # delete the downloaded files so that the final combined file remain
            try:
                os.remove(last_vid_file)
                os.remove(last_audio_file)
            except OSError:
                pass

        # endif
        print("\nDownload is complete. Enjoy!\n")


    def download_audio(self, path_to_save=None) -> None:
        """
        Downloads only the audio from the video. 
        Format: .mp3

        (Useful when downloading songs from YouTube)
        """
        audio_src_url: str = ""
        for audio_stream in self._audio_streams:
            # apparently YT serves medium quality audio as its highest quality
            if audio_stream["audio_quality"] == "AUDIO_QUALITY_MEDIUM":
                audio_src_url: str = audio_stream["src_url"]
                break

        # clean the url first
        audio_src_url: str = utils.sanitize_url(audio_src_url)

        print("::-> Downloading the audio file...")
        # request the audio source
        try:
            audio_resp: requests.Response = requests.get(audio_src_url, headers=utils.request_headers(), stream=True)
            audio_resp.raise_for_status()
        except:
            print("::-> An error occurred while requesting the file")
            raise

        # save to disk with is_video not set
        utils.save_to_disk(audio_resp, self.get_video_title(), path_to_save, is_video=False)
        print("Done!\n")
