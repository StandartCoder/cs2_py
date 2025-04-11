import json
from pathlib import Path
from datetime import datetime

class Config:
    def __init__(self, path="config.json"):
        self.path = Path(path)
        self.data = {
            "debug": False,
            "target_process": "cs2.exe",
            "dll_name": "python311.dll"
        }
        self._load()

    def _load(self):
        now = datetime.now().strftime("%H:%M:%S")
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
            except Exception as e:
                
                print(f"[{now}] [WARN] Failed to load config: {e} – using defaults")
        else:
            print(f"[{now}] [WARN] Config file not found – using defaults")
            self._save()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def is_debug(self):
        return bool(self.data.get("debug", False))

config = Config()
