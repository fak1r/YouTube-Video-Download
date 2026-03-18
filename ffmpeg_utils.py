from pathlib import Path
import os
import shutil


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


def build_unique_output_path(directory: Path, stem: str, suffix: str) -> Path:
    clean_stem = stem.strip().rstrip(".") or "output"
    candidate = directory / f"{clean_stem}{suffix}"
    index = 1

    while candidate.exists():
        candidate = directory / f"{clean_stem} ({index}){suffix}"
        index += 1

    return candidate
