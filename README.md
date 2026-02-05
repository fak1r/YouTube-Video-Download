# YouTube Download (local)

Simple CLI for downloading a YouTube video to the local `video` folder with a chosen quality.

## Setup
1. `python -m venv .venv`
2. `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Install ffmpeg and make sure it is in PATH (required to merge video+audio).

## Run
`python videoDownload.py`

Downloads are saved into `./video`.

## Notes
- If the exact quality is not available, the script chooses the nearest lower quality or the highest available.
- Respect copyright and platform rules.
