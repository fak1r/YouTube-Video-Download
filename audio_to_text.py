from pathlib import Path
import os
import sys


ROOT_DIR = Path(__file__).resolve().parent
AUDIO_DIR = ROOT_DIR / "audio"
TEXT_DIR = ROOT_DIR / "text"
MODEL_SIZE = os.environ.get("WHISPER_MODEL", "base")
INITIAL_PROMPT = (
    "Russian speech. English words may appear as programming terms."
)


def normalize_input_path(raw_path: str):
    cleaned = raw_path.strip().strip('"').strip("'")
    if not cleaned:
        return None

    audio_path = Path(cleaned).expanduser()
    candidates = [audio_path]

    if audio_path.suffix.lower() != ".mp3":
        candidates.append(audio_path.with_suffix(".mp3"))

    if not audio_path.is_absolute():
        candidates.append(AUDIO_DIR / audio_path)
        if audio_path.suffix.lower() != ".mp3":
            candidates.append(AUDIO_DIR / audio_path.with_suffix(".mp3"))

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return audio_path


def ask_audio_path():
    try:
        raw_path = input("Paste MP3 path or file name from ./audio: ").strip()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return None

    audio_path = normalize_input_path(raw_path)
    if audio_path is None:
        print("Path is required.")
        return None

    if not audio_path.exists():
        print("File not found.")
        return None

    if not audio_path.is_file():
        print("Path must point to a file.")
        return None

    if audio_path.suffix.lower() != ".mp3":
        print("Only MP3 files are supported.")
        return None

    return audio_path


def load_whisper_model():
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Missing dependency: faster-whisper. Install with: pip install -r requirements.txt")
        return None

    print(f"Loading model: {MODEL_SIZE}")
    print("First run may take a few minutes: model files can be downloaded and initialized on CPU.")

    try:
        model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    except KeyboardInterrupt:
        print("\nModel loading cancelled.")
        return None
    except Exception as exc:
        print(f"Failed to load model: {exc}")
        return None

    print("Model loaded.")
    return model


def transcribe_audio(audio_path: Path) -> int:
    model = load_whisper_model()
    if model is None:
        return 1

    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TEXT_DIR / f"{audio_path.stem}.txt"

    print(f"Source: {audio_path}")
    print(f"Output: {output_path}")
    print("Starting transcription...")

    try:
        segments, info = model.transcribe(
            str(audio_path),
            language="ru",
            beam_size=5,
            vad_filter=True,
            initial_prompt=INITIAL_PROMPT,
        )
    except KeyboardInterrupt:
        print("\nTranscription cancelled.")
        return 1
    except Exception as exc:
        print(f"Transcription failed: {exc}")
        return 1

    print(f"Detected language: {info.language}")

    parts = []
    segment_count = 0
    try:
        for segment in segments:
            text = segment.text.strip()
            if text:
                parts.append(text)
                segment_count += 1
                print(f"[{segment_count}] {text}")
    except KeyboardInterrupt:
        print("\nTranscription cancelled.")
        return 1

    transcript = "\n".join(parts).strip()
    if not transcript:
        print("No speech recognized.")
        return 1

    output_path.write_text(transcript + "\n", encoding="utf-8")
    print(f"Saved: {output_path}")
    return 0


def main() -> int:
    audio_path = ask_audio_path()
    if audio_path is None:
        return 1
    return transcribe_audio(audio_path)


if __name__ == "__main__":
    sys.exit(main())
