# YouTube Download (local)

Simple CLI for downloading YouTube content to local folders.

## Setup
1. `python -m venv .venv`
2. `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Install ffmpeg and make sure it is in PATH (required to merge video+audio).

## Run
`python youtube_downloader.py`

To extract audio from a local video file into MP3:
`python video_to_mp3.py`

Downloads are saved into:
- `video` mode -> `./video`
- `audio` mode -> `./audio`

`video_to_mp3.py` saves MP3 files into `./audio`.

## Notes
- The script supports two modes: `video` and `audio`.
- `audio` mode saves MP3 when ffmpeg is available, otherwise it saves the original audio stream format.
- `video_to_mp3.py` extracts audio from a local video file and saves it as MP3.
- If the exact quality is not available, the script chooses the nearest lower quality or the highest available.
- Respect copyright and platform rules.
