#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import youtubedownload

parser = argparse.ArgumentParser(
    description="Download YouTube videos using the CLI itself"
)
excl_group = parser.add_mutually_exclusive_group()
excl_group.add_argument(
    "-a",
    "--onlyaudio",
    action="store_true",
    help="Downloads only the audio from the YouTube URL",
)
excl_group.add_argument(
    "-q", "--quality", type=str, help="The quality to download the video in"
)

parser.add_argument(
    "VIDEO_URL", type=str, help="The URL of the video which is to be downloaded"
)
parser.add_argument(
    "-p", "--path", type=str, help="The path where the video/audio should be downloaded"
)

# parse the args
args = parser.parse_args()

ytvideo = youtubedownload.YouTubeDownLoad(args.VIDEO_URL)
# when path is not provided, it will download in current directory
if not args.path:
    args.path = "."
if args.onlyaudio:
    ytvideo.download_audio(args.path)
else:
    ytvideo.download(args.quality, args.path)
