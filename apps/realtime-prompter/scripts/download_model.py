"""Download a selected official Vosk model during initial setup only."""

import argparse
import hashlib
from pathlib import Path
import shutil
import tempfile
import urllib.request
import zipfile

MODELS = {"ja": "vosk-model-small-ja-0.22", "en": "vosk-model-small-en-us-0.15"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=MODELS, default="ja")
    args = parser.parse_args()
    name = MODELS[args.language]
    output = Path(__file__).resolve().parent.parent / "models"
    output.mkdir(exist_ok=True)
    target = output / name
    if target.is_dir():
        print(f"Already installed: {target}")
        return
    url = f"https://alphacephei.com/vosk/models/{name}.zip"
    print(f"Downloading {url}", flush=True)
    with tempfile.TemporaryDirectory(dir=output) as temp:
        archive = Path(temp) / "model.zip"
        with urllib.request.urlopen(url, timeout=60) as response, archive.open("wb") as dest:
            shutil.copyfileobj(response, dest)
        print(f"Downloaded archive SHA256: {hashlib.sha256(archive.read_bytes()).hexdigest()}")
        with zipfile.ZipFile(archive) as zipped:
            for info in zipped.infolist():
                parts = Path(info.filename).parts
                if not parts or parts[0] != name or ".." in parts or info.filename.startswith("/"):
                    raise ValueError("Unexpected archive path")
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Archive symlinks are not supported")
            zipped.extractall(temp)
        (Path(temp) / name).rename(target)
    print(f"VOSK_MODEL_PATH={target}")


if __name__ == "__main__":
    main()
