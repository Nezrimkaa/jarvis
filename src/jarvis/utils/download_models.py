"""Download required models for Jarvis Assistant.

Usage:
    python -m jarvis.utils.download_models
    python -m jarvis.utils.download_models --stt-only
    python -m jarvis.utils.download_models --tts-only
"""

import argparse
import os
import zipfile
import urllib.request
from pathlib import Path
from typing import Optional


MODELS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "models"

VOSK_URL = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
VOSK_DIR = "vosk-model-small-ru-0.22"

PIPER_VOICE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx"
PIPER_CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json"
PIPER_DIR = "piper-voices"


def download_file(url: str, dest: Path, desc: str = "") -> bool:
    """Download a file with progress indication."""
    try:
        print(f"Downloading {desc or os.path.basename(url)}...")

        def report(block_num, block_size, total_size):
            downloaded = block_num * block_size / (1024 * 1024)
            total = total_size / (1024 * 1024) if total_size > 0 else 0
            if total > 0:
                print(f"  {downloaded:.1f} / {total:.1f} MB ({downloaded/total*100:.0f}%)", end="\r")
            else:
                print(f"  {downloaded:.1f} MB", end="\r")

        urllib.request.urlretrieve(url, dest, reporthook=report)
        print()
        return True
    except Exception as e:
        print(f"  Failed: {e}")
        return False


def download_vosk():
    """Download and extract Vosk speech recognition model."""
    vosk_dir = MODELS_DIR / VOSK_DIR
    if vosk_dir.exists():
        print(f"Vosk model already exists at {vosk_dir}")
        return True

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = MODELS_DIR / "vosk.zip"

    success = download_file(VOSK_URL, zip_path, "Vosk Russian model (~50MB)")
    if not success:
        return False

    print("Extracting...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(MODELS_DIR)
    zip_path.unlink()
    print(f"Vosk model extracted to {vosk_dir}")
    return True


def download_piper():
    """Download Piper TTS voice model."""
    piper_dir = MODELS_DIR / PIPER_DIR
    piper_dir.mkdir(parents=True, exist_ok=True)

    model_file = piper_dir / "ru_RU-irina-medium.onnx"
    config_file = piper_dir / "ru_RU-irina-medium.onnx.json"

    if model_file.exists() and config_file.exists():
        print(f"Piper voice already exists at {piper_dir}")
        return True

    onnx_ok = True
    json_ok = True

    if not model_file.exists():
        onnx_ok = download_file(PIPER_VOICE_URL, model_file, "Piper voice model (~40MB)")
    if onnx_ok and not config_file.exists():
        json_ok = download_file(PIPER_CONFIG_URL, config_file, "Piper config")

    return onnx_ok and json_ok


def main():
    parser = argparse.ArgumentParser(description="Download models for Jarvis Assistant")
    parser.add_argument("--stt-only", action="store_true", help="Download only STT (Vosk) model")
    parser.add_argument("--tts-only", action="store_true", help="Download only TTS (Piper) model")
    args = parser.parse_args()

    print(f"Models directory: {MODELS_DIR}")

    if args.tts_only:
        download_piper()
    elif args.stt_only:
        download_vosk()
    else:
        download_vosk()
        download_piper()

    print("Done!")


if __name__ == "__main__":
    main()
