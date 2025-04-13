import sys
import os
import ctypes
import importlib
import traceback

BASE_PATH = "{{BASE_PATH}}\\cs2"

try:
    with open("cs2_loader_log.txt", "w") as f:
        f.write(f"Starting CS2.py loader\n")
        f.write(f"BASE_PATH: {BASE_PATH}\n")
        f.write(f"Current working directory: {os.getcwd()}\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"System path: {sys.path}\n")
except Exception as e:
    ctypes.windll.user32.MessageBoxW(None, f"Failed to create log: {e}", "Log Error", 0)

sys.path.append(BASE_PATH)
sys.path.append(os.path.dirname(BASE_PATH))

try:
    with open("cs2_loader_log.txt", "a") as f:
        f.write(f"Reloading cs2 modules...\n")
        
    for name in list(sys.modules):
        try:
            if name == "cs2" or name.startswith("cs2."):
                importlib.reload(sys.modules[name])
                with open("cs2_loader_log.txt", "a") as f:
                    f.write(f"Reloaded module: {name}\n")
        except Exception as ex:
            with open("cs2_loader_log.txt", "a") as f:
                f.write(f"Failed to reload {name}: {ex}\n")
            pass

    with open("cs2_loader_log.txt", "a") as f:
        f.write(f"Importing main cs2 module...\n")
    
    import cs2
    
    with open("cs2_loader_log.txt", "a") as f:
        f.write(f"Running cs2.run()...\n")
    
    cs2.run()
    
    with open("cs2_loader_log.txt", "a") as f:
        f.write(f"cs2.run() completed successfully\n")

except Exception as e:
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    
    try:
        with open("cs2_loader_error.txt", "w") as f:
            f.write(f"CS2 Import/Run Error: {e}\n")
            f.write(f"Traceback:\n{tb_str}\n")
    except:
        pass
    
    ctypes.windll.user32.MessageBoxW(None, f"CS2 Import/Run Error: {e}\nSee cs2_loader_error.txt for details", "FAIL", 0)
