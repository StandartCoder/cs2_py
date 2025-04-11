import ctypes
import os

def get_process_name():
    GetModuleFileNameW = ctypes.windll.kernel32.GetModuleFileNameW
    GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32]
    GetModuleFileNameW.restype = ctypes.c_uint32

    buffer = ctypes.create_unicode_buffer(260)
    GetModuleFileNameW(None, buffer, 260)
    return os.path.basename(buffer.value)

def run():
    pname = get_process_name()
    ctypes.windll.user32.MessageBoxW(None, f"Running insides: {pname}", "CS2 Internal Check", 0)