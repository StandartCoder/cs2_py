from ctypes import wintypes
import ctypes
from lib import winapi, utility, injector
from pathlib import Path

from lib.debug import log, success, error, warn, debug
from lib.config import config

target = config.get("target_process")
dll_name = config.get("dll_name")

def runCode(pid, codeStr):
    base = utility.modBase(pid, dll_name)
    if base is None:
        error(dll_name + " not loaded in target process – make sure it's injected first")
        exit(1)

    debug(f"{dll_name} base address in target process: 0x{base:X}")

    handle = wintypes.HANDLE(
        winapi.OpenProcess(winapi.PROCESS_ALL_ACCESS, 0, wintypes.DWORD(pid))
    )
    if not handle:
        error("Failed to open target process handle")
        exit(1)

    Py_InitializeEx = utility.getRemoteProcAddr(handle, base, "Py_InitializeEx")
    PyRun_SimpleString = utility.getRemoteProcAddr(handle, base, "PyRun_SimpleString")

    if not Py_InitializeEx or not PyRun_SimpleString:
        error("Failed to locate Py_InitializeEx or PyRun_SimpleString in remote process")
        exit(1)

    debug(f"Py_InitializeEx: 0x{Py_InitializeEx:X}")
    debug(f"PyRun_SimpleString: 0x{PyRun_SimpleString:X}")

    debug("Creating remote thread for Py_InitializeEx...")
    pyinit = winapi.CreateRemoteThread(
        handle,
        None,
        0,
        wintypes.LPVOID(Py_InitializeEx),
        0,
        0,
        None
    )
    if not pyinit:
        error("CreateRemoteThread for Py_InitializeEx failed")
        winapi.CloseHandle(handle)
        exit(1)

    winapi.WaitForSingleObject(pyinit, wintypes.DWORD(10000))

    codeStr = codeStr.replace("{{BASE_PATH}}", str(Path(".").resolve()))
    codeStr = codeStr.encode("utf-8") + b"\x00"

    debug("Allocating remote memory for Python code...")
    codeAddr = winapi.VirtualAllocEx(
        handle,
        winapi.NULL,
        len(codeStr),
        winapi.MEM_RESERVE | winapi.MEM_COMMIT,
        winapi.PAGE_EXECUTE_READWRITE
    )
    if not codeAddr:
        error("VirtualAllocEx for code string failed")
        winapi.CloseHandle(handle)
        exit(1)

    debug(f"Writing Python code into remote memory at 0x{codeAddr:X}")
    codeWritten = winapi.WriteProcessMemory(
        handle,
        codeAddr,
        codeStr,
        len(codeStr),
        ctypes.cast(0, ctypes.POINTER(ctypes.c_size_t))
    )
    if not codeWritten:
        error("WriteProcessMemory failed for Python code")
        winapi.CloseHandle(handle)
        exit(1)

    debug("Creating remote thread to run Python code...")
    pyexec = winapi.CreateRemoteThread(
        handle,
        None,
        0,
        wintypes.LPVOID(PyRun_SimpleString),
        codeAddr,
        0,
        None
    )
    if not pyexec:
        error("CreateRemoteThread for Python code failed")
    else:
        success("Python code executed via remote thread")

    winapi.CloseHandle(handle)
    log("Injection sequence completed")

def loadCode(pth):
    log(f"Loading code from file: {pth}")
    try:
        return open(pth, "r", encoding="utf-8").read()
    except Exception as e:
        error(f"Failed to read file '{pth}': {e}")
        exit(1)

log("Searching for '" + target + "' process...")
pid = utility.getPID(target)
if pid is None:
    error("Target process '" + target + "' not found – aborting")
    exit(1)

log("Injecting " + dll_name +" into target process...")
dll_path = str(Path(dll_name).resolve()).encode("utf-8") + b"\x00"
injector.inject(dll_path, pid)
success("DLL injection routine complete")

codeStr = loadCode("cs2_loader.py")
runCode(pid, codeStr)