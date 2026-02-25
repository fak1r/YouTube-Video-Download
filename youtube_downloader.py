from pathlib import Path
import os
import shutil
import sys

try:
    import yt_dlp
except ImportError:
    print("Missing dependency: yt-dlp. Install with: pip install -r requirements.txt")
    sys.exit(1)

VIDEO_DIR = Path(__file__).resolve().parent / "video"
AUDIO_DIR = Path(__file__).resolve().parent / "audio"


def resolve_ffmpeg():
    env_path = os.environ.get("FFMPEG_PATH")
    if env_path:
        p = Path(env_path)
        if p.is_dir():
            candidate = p / "ffmpeg.exe"
            if candidate.exists():
                return str(candidate)
        if p.exists():
            return str(p)

    env_home = os.environ.get("FFMPEG_HOME")
    if env_home:
        p = Path(env_home) / "bin" / "ffmpeg.exe"
        if p.exists():
            return str(p)

    found = shutil.which("ffmpeg")
    if found:
        return found

    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        link = Path(localappdata) / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe"
        if link.exists():
            return str(link)

        packages = Path(localappdata) / "Microsoft" / "WinGet" / "Packages"
        if packages.exists():
            prefixes = (
                "yt-dlp.FFmpeg",
                "Gyan.FFmpeg",
                "BtbN.FFmpeg",
                "Jellyfin.FFmpeg",
            )
            for pkg in packages.iterdir():
                if not pkg.is_dir() or not pkg.name.startswith(prefixes):
                    continue
                for candidate in pkg.rglob("ffmpeg.exe"):
                    return str(candidate)

    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if not base:
            continue
        for name in ("FFmpeg", "ffmpeg"):
            candidate = Path(base) / name / "bin" / "ffmpeg.exe"
            if candidate.exists():
                return str(candidate)

    return None


def normalize_url(url: str):
    url = url.strip()
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        return None
    return url


def choose_mode() -> str:
    mode = input("Download mode: video or audio? [v/a, default v]: ").strip().lower()
    if mode in ("", "v", "video"):
        return "video"
    if mode in ("a", "audio"):
        return "audio"
    print("Invalid mode. Using video mode.")
    return "video"


def get_info(url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def available_heights(info: dict):
    heights = set()
    for f in info.get("formats", []):
        if f.get("vcodec") == "none":
            continue
        h = f.get("height")
        if isinstance(h, int):
            heights.add(h)
    return sorted(heights, reverse=True)


def choose_format(heights):
    if not heights:
        print("Could not detect available qualities. Downloading best available.")
        return "bestvideo+bestaudio/best"

    print("Available qualities:", ", ".join(f"{h}p" for h in heights))
    desired = input("Enter desired quality (e.g., 720 or 720p) or press Enter for best: ").strip()
    if desired.lower().endswith("p"):
        desired = desired[:-1].strip()

    if not desired:
        return "bestvideo+bestaudio/best"
    if not desired.isdigit():
        print("Invalid input. Downloading best available.")
        return "bestvideo+bestaudio/best"

    target = int(desired)
    if target in heights:
        return f"bestvideo[height={target}]+bestaudio/best[height={target}]/best"

    lower = [h for h in heights if h < target]
    if lower:
        chosen = lower[0]
        print(f"{target}p not available. Using {chosen}p.")
        return f"bestvideo[height={chosen}]+bestaudio/best[height={chosen}]/best"

    chosen = heights[0]
    print(f"{target}p not available. Using highest {chosen}p.")
    return f"bestvideo[height={chosen}]+bestaudio/best[height={chosen}]/best"


def progress_hook(d: dict) -> None:
    status = d.get("status")
    if status == "finished":
        filename = d.get("filename")
        if filename:
            print(f"Saved: {filename}")
        else:
            print("Download finished.")


def download(url: str, mode: str) -> None:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg_path = resolve_ffmpeg()

    if mode == "audio":
        ydl_opts = {
            "outtmpl": str(AUDIO_DIR / "%(title).200s.%(ext)s"),
            "format": "bestaudio/best",
            "noplaylist": True,
            "progress_hooks": [progress_hook],
        }
        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = ffmpeg_path
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
            print(f"Using ffmpeg: {ffmpeg_path}")
            print("Mode: audio only (mp3).")
        else:
            print("ffmpeg not found in PATH or common locations.")
            print("Mode: audio only (original format without conversion).")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return

    info = get_info(url)
    heights = available_heights(info)
    format_selector = choose_format(heights)
    ydl_opts = {
        "outtmpl": str(VIDEO_DIR / "%(title).200s.%(ext)s"),
        "format": format_selector,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "progress_hooks": [progress_hook],
    }
    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = ffmpeg_path
        print(f"Using ffmpeg: {ffmpeg_path}")
    else:
        print("ffmpeg not found in PATH or common locations.")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main() -> int:
    mode = choose_mode()

    try:
        url = input("Paste YouTube URL: ").strip()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 1

    url = normalize_url(url)
    if not url:
        print("Please provide a valid URL starting with http:// or https://")
        return 1

    try:
        download(url, mode)
    except yt_dlp.utils.DownloadError as exc:
        msg = str(exc)
        print(f"Download failed: {msg}")
        if "ffmpeg is not installed" in msg.lower():
            print("Hint: set FFMPEG_PATH to your ffmpeg.exe path or add ffmpeg to PATH.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
