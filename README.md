## YouTube Video Downloader

- Download YouTube video(s)/audio(s) through the CLI
- Pass in the `VIDEO_URL` as an argument with the `-p path/to/save` and the `--onlyaudio` option
  to download the only the audio, from the video, and save it in `path/to/save`
- Helpful in download of songs from YouTube (something which I do a lot)

### Usage

Clone the repo locally

```
$ git clone https://github.com/Maharshi-Pandya/YouTube-Downloader.git
$ cd YouTube-Downloader
```

We have to pass in some arguments in the CLI for this to work

- --onlyaudio or -q (--quality)
- VIDEO_URL
- -p (--path) path/to/save

Eg.

```
$ ./app.py --onlyaudio -p <path/to/save> <YouTube_VIDEO_URL>
```

Downloads only the audio from the YouTube video URL specified

Also,

```
$ ./app.py -q 360p -p <path/to/save> <YouTube_VIDEO_URL>
```

Downloads the video in 360p quality and saves it to `path/to/save`

##### NOTE

In some of the YouTube videos (eg. videos of VEVO), their source urls are encrypted with some signature cipher.
The source urls cannot be fetched without getting the signature from the cipher. (YouTube constantly
changes the algorithm in their JS files)
Currently, this YouTube-Downloader doesnot support that.

And it gives out this error

```
::-> Fetching the video data
::-> Extracted video information
::-> Detected signature ciphers in the video data
Error: Unable to start the download
```
