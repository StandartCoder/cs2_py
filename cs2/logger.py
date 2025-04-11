import ctypes
import sys
import os
import traceback
from datetime import datetime
from pathlib import Path

class Logger:
    LEVELS = {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3,
        "CRITICAL": 4,
    }

    def __init__(self, log_path="cs2py_log.txt", show_messagebox=True, level="INFO"):
        self.level = self.LEVELS.get(level.upper(), 1)
        self.show_messagebox = show_messagebox
        self.log_path = Path(log_path)

        try:
            with self.log_path.open("w", encoding="utf-8") as log_file:
                log_file.write(f"[{self._timestamp()}] [INIT] Logger started at {datetime.now()}\n")
        except Exception:
            fallback_path = Path(os.environ.get("TEMP", ".")) / "cs2py_log.txt"
            self.log_path = fallback_path
            with self.log_path.open("w", encoding="utf-8") as log_file:
                log_file.write(f"[{self._timestamp()}] [INIT] Logger fallback started at {datetime.now()}\n")

    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def _log(self, level, message):
        try:
            with self.log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(f"[{self._timestamp()}] [{level}] {message}\n")
        except Exception:
            pass

    def _show_box(self, title, msg):
        if self.show_messagebox:
            try:
                ctypes.windll.user32.MessageBoxW(None, str(msg), str(title), 0)
            except Exception:
                pass

    def debug(self, message):
        if self.level <= self.LEVELS["DEBUG"]:
            self._log("DEBUG", message)

    def info(self, message):
        if self.level <= self.LEVELS["INFO"]:
            self._log("INFO", message)

    def warning(self, message):
        if self.level <= self.LEVELS["WARNING"]:
            self._log("WARNING", message)
            self._show_box("CS2_PY Warning", message)

    def error(self, message):
        if self.level <= self.LEVELS["ERROR"]:
            self._log("ERROR", message)
            self._show_box("CS2_PY Error", message)

    def critical(self, message):
        if self.level <= self.LEVELS["CRITICAL"]:
            self._log("CRITICAL", message)
            self._show_box("CS2_PY CRITICAL ERROR", message)

    def exception(self, message=""):
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        full_message = f"{message}\n{tb_str}" if message else tb_str
        self.error(full_message)

logger = Logger()
