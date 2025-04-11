import ctypes
import ctypes.wintypes as wintypes
from pathlib import Path
from lib import winapi
from lib.debug import log, success, error, warn, debug

def inject(dll_path: bytes, pid: int):
    dll_name = Path(dll_path.decode(errors='ignore')).name
    debug(f"[*] Attempting injection into PID {pid} with DLL: {dll_name}")

    if not dll_path.endswith(b'\x00'):
        dll_path += b'\x00'

    handle = winapi.OpenProcess(winapi.PROCESS_ALL_ACCESS, False, pid)
    if not handle:
        return error(f"OpenProcess failed – LastError={ctypes.get_last_error()}")

    debug("[*] Allocating memory in target process...")
    alloc_ptr = winapi.VirtualAllocEx(
        handle,
        None,
        len(dll_path),
        winapi.MEM_RESERVE | winapi.MEM_COMMIT,
        winapi.PAGE_EXECUTE_READWRITE
    )

    if not alloc_ptr:
        winapi.CloseHandle(handle)
        return error(f"VirtualAllocEx failed – LastError={ctypes.get_last_error()}")

    alloc = ctypes.c_void_p(alloc_ptr)
    if not alloc.value:
        winapi.CloseHandle(handle)
        return error(f"VirtualAllocEx returned NULL pointer – LastError={ctypes.get_last_error()}")

    debug(f"[+] Memory allocated at address: 0x{alloc.value:X}")

    debug("[*] Writing DLL path to allocated memory...")
    success_write = winapi.WriteProcessMemory(
        handle,
        alloc,
        dll_path,
        len(dll_path),
        None
    )

    if not success_write:
        winapi.CloseHandle(handle)
        return error(f"WriteProcessMemory failed – LastError={ctypes.get_last_error()}")

    debug("[+] DLL path written successfully")

    debug("[*] Creating remote thread with LoadLibraryA...")
    thread = winapi.CreateRemoteThread(handle, None, 0, winapi.LoadLibraryA, alloc, 0, None)

    if not thread:
        error(f"CreateRemoteThread failed – LastError={ctypes.get_last_error()}")
    else:
        debug("[+] Remote thread created – DLL should now be loading")
        winapi.WaitForSingleObject(thread, 10000)

    winapi.CloseHandle(handle)
