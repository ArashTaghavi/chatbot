from pathlib import Path


def load(file_path: str):
    path = Path(file_path)

    return path.read_text("utf-8-sig").splitlines()
