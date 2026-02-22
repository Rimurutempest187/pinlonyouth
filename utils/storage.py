import json
import threading
from pathlib import Path
from typing import Any
from shutil import copy2

lock = threading.Lock()

def load_data(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with lock:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

def save_data(path: str, data: dict) -> None:
    p = Path(path)
    with lock:
        with p.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def backup_data(path: str, backup_path: str) -> None:
    copy2(path, backup_path)

def restore_data(backup_path: str, path: str) -> None:
    copy2(backup_path, path)
