#!/mnt/sda1/Codes/Python/youtube_download/bin/python3
# -*- coding: utf-8 -*-

import argparse
import youtubedownload

parser = argparse.ArgumentParser(
    description="Download YouTube videos using the CLI itself"
)

parser.add_argument("--onlyaudio", action="store_true", help="Downloads only the audio from the YouTube URL")
parser.add_argument("VIDEO_URL", type=str, help="The URL of the video which is to be downloaded")
parser.add_argument("-p", "--path", type=str, help="The path where the video/audio should be downloaded")

args = parser.parse_args()

ytvideo = youtubedownload.YouTubeDownLoad(args.VIDEO_URL)
if args.onlyaudio:
    ytvideo.download_audio(args.path)
