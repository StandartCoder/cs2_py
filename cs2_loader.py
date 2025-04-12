import sys
import os
import ctypes
import importlib

BASE_PATH = "{{BASE_PATH}}\\cs2"
ctypes.windll.user32.MessageBoxW(None, f"Python loading: {BASE_PATH}", "Injected", 0)

sys.path.append(BASE_PATH)
sys.path.append(os.path.dirname(BASE_PATH))

try:
    for name in list(sys.modules):
        try:
            if name.startswith("cs2"):
                importlib.reload(sys.modules[name])
        except:
            pass  

    import cs2
    cs2.run()

except Exception as e:
    ctypes.windll.user32.MessageBoxW(None, f"CS2 Import Error: {e}", "FAIL", 0)
