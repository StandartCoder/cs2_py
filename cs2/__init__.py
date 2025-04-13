import ctypes
from cs2.logger import logger
from cs2.hook import dx_hook

def run():
    try:
        logger.info("Initializing CS2 internal Python module")
        dx_hook.initialize_hook()
        logger.info("Hook successfully installed")
        ctypes.windll.user32.MessageBoxW(None, "Hook installed successfully!", "CS2_PY", 0)
    except Exception as e:
        logger.exception("Failed to initialize CS2 Python internal module")
        ctypes.windll.user32.MessageBoxW(None, f"CS2 Init Error:\n{e}", "CS2_PY ERROR", 0)