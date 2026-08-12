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

To convert an MP3 file into text:
`python audio_to_text.py`

Downloads are saved into:
- `video` mode -> `./video`
- `audio` mode -> `./audio`

`video_to_mp3.py` saves MP3 files into `./audio`.
`audio_to_text.py` saves transcripts into `./text`.

## Notes
- The script supports two modes: `video` and `audio`.
- If YouTube asks you to sign in or confirm you are not a bot, run the downloader again and enter your signed-in browser name at the `Cookies` prompt, for example `chrome`, `edge`, `firefox`, or `brave`.
- `audio` mode saves MP3 when ffmpeg is available, otherwise it saves the original audio stream format.
- `video_to_mp3.py` extracts audio from a local video file and saves it as MP3.
- `audio_to_text.py` transcribes MP3 files into UTF-8 text with Russian selected as the transcription language.
- The first run of `audio_to_text.py` may download the speech model.
- For slower CPUs in PowerShell, you can choose a lighter model before launch, for example: `$env:WHISPER_MODEL="tiny"` or `$env:WHISPER_MODEL="base"`.
- If the exact quality is not available, the script chooses the nearest lower quality or the highest available.
- Respect copyright and platform rules.
