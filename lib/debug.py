from datetime import datetime
from lib.config import config

def log(msg: str, level="INFO"):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{level.upper()}] {msg}")

def success(msg: str):
    log(msg, "SUCCESS")

def error(msg: str):
    log(msg, "ERROR")

def warn(msg: str):
    log(msg, "WARNING")

def debug(msg: str):
    if config.is_debug():
        log(msg, "DEBUG")