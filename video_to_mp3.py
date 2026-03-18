from pathlib import Path
import subprocess
import sys

from ffmpeg_utils import build_unique_output_path, resolve_ffmpeg


AUDIO_DIR = Path(__file__).resolve().parent / "audio"


def normalize_input_path(raw_path: str):
    cleaned = raw_path.strip().strip('"').strip("'")
    if not cleaned:
        return None
    return Path(cleaned).expanduser()


def ask_video_path():
    try:
        raw_path = input("Paste local video file path: ").strip()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return None

    video_path = normalize_input_path(raw_path)
    if video_path is None:
        print("Path is required.")
        return None

    if not video_path.exists():
        print("File not found.")
        return None

    if not video_path.is_file():
        print("Path must point to a file.")
        return None

    return video_path


def extract_audio(video_path: Path) -> int:
    ffmpeg_path = resolve_ffmpeg()
    if not ffmpeg_path:
        print("ffmpeg not found in PATH or common locations.")
        print("Install ffmpeg first, then try again.")
        return 1

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    output_path = build_unique_output_path(AUDIO_DIR, video_path.stem, ".mp3")

    command = [
        ffmpeg_path,
        "-i",
        str(video_path),
        "-vn",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(output_path),
    ]

    print(f"Using ffmpeg: {ffmpeg_path}")
    print(f"Source: {video_path}")
    print(f"Output: {output_path}")

    result = subprocess.run(command)
    if result.returncode != 0:
        print("Audio extraction failed.")
        return result.returncode

    print(f"Saved: {output_path}")
    return 0


def main() -> int:
    video_path = ask_video_path()
    if video_path is None:
        return 1
    return extract_audio(video_path)


if __name__ == "__main__":
    sys.exit(main())
