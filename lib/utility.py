from lib.debug import log, success, error, warn, debug

import ctypes
import psutil
from lib import winapi
from ctypes import wintypes

if not hasattr(wintypes, 'SIZE_T'):
    wintypes.SIZE_T = ctypes.c_size_t

def getPID(proc_name):
    from lib.debug import success, warn
    for proc in psutil.process_iter():
        try:
            if proc_name.lower() in proc.name().lower():
                success(f"Found process '{proc_name}' with PID {proc.pid}")
                return proc.pid
        except Exception as e:
            warn(f"Error while iterating processes: {e}")
    warn(f"Process '{proc_name}' not found")
    return None

def modBase(pid, mod_name):
    from lib.debug import log, error, success
    base_addr = None
    hSnapshot = winapi.CreateToolhelp32Snapshot(winapi.TH32CS_SNAPMODULE | winapi.TH32CS_SNAPMODULE32, pid)
    debug(f"Searching for module '{mod_name}' in PID {pid}")

    if (hSnapshot != winapi.INVALID_HANDLE_VALUE):
        mod_entry = winapi.MODULEENTRY32()
        mod_entry.dwSize = ctypes.sizeof(winapi.MODULEENTRY32)

        if winapi.Module32First(hSnapshot, ctypes.byref(mod_entry)):
            while True:
                module_name = mod_entry.szModule.decode(errors="ignore")
                if module_name.lower() == mod_name.lower():
                    base_addr = int(hex(ctypes.addressof(mod_entry.modBaseAddr.contents)), 16)
                    debug(f"Found base address of '{mod_name}': 0x{base_addr:X}")
                    break
                if not winapi.Module32Next(hSnapshot, ctypes.byref(mod_entry)):
                    break

    winapi.CloseHandle(hSnapshot)
    if base_addr is None:
        error(f"Module '{mod_name}' not found in process {pid}")
    return base_addr

def read_remote_memory(process_handle, address, size):
    buffer = ctypes.create_string_buffer(size)
    bytes_read = wintypes.SIZE_T(0)
    success = winapi.api.ReadProcessMemory(
        process_handle,
        wintypes.LPCVOID(address),
        buffer,
        size,
        ctypes.byref(bytes_read)
    )
    if not success:
        error(f"ReadProcessMemory failed at address 0x{address:X}")
        return None
    return buffer.raw

def read_remote_string(process_handle,addr,max_len=128):
    raw_data = read_remote_memory(process_handle, addr, max_len)
    if not raw_data:
        return ""
    return raw_data.split(b'\x00', 1)[0].decode(errors='ignore')

def getRemoteProcAddr(proc_handle, mod_base, func_name):
    if mod_base == 0:
        error("Module base address is 0")
        return 0

    debug(f"Resolving remote procedure '{func_name}' in module at 0x{mod_base:X}")

    dos_header = read_remote_memory(proc_handle, mod_base, 0x40)
    if not dos_header:
        error("Failed to read DOS header")
        return 0

    e_lfanew = int.from_bytes(dos_header[0x3C:0x3C+4], "little")
    debug(f"e_lfanew = 0x{e_lfanew:X}")

    pe_header = read_remote_memory(proc_handle, mod_base + e_lfanew, 0x200)
    if not pe_header:
        error("Failed to read PE header")
        return 0

    sign = int.from_bytes(pe_header[0:4], "little")
    if sign != 0x00004550:
        error(f"Invalid PE signature: 0x{sign:X}")
        return 0

    magic = int.from_bytes(pe_header[0x18:0x1A], "little")
    is32 = (magic == 0x10b)
    is64 = (magic == 0x20b)
    debug(f"PE format: {'PE32' if is32 else 'PE32+' if is64 else 'Unknown'}")

    if not (is32 or is64):
        error(f"Unsupported PE magic: 0x{magic:X}")
        return 0

    data_dir_offset = 0x60 if is32 else 0x70
    export_rva = int.from_bytes(pe_header[0x18 + data_dir_offset:0x1C + data_dir_offset], "little")
    debug(f"Export Table RVA: 0x{export_rva:X}")

    if export_rva == 0:
        error("Export table RVA is 0 – no exports available")
        return 0

    export_table_ptr = mod_base + export_rva
    export_table = read_remote_memory(proc_handle, export_table_ptr, 40)
    if not export_table:
        error("Failed to read export table")
        return 0

    num_funcs = int.from_bytes(export_table[0x14:0x18], "little")
    num_names = int.from_bytes(export_table[0x18:0x1C], "little")
    addr_funcs_rva = int.from_bytes(export_table[0x1C:0x20], "little")
    addr_names_rva = int.from_bytes(export_table[0x20:0x24], "little")
    addr_ordinals_rva = int.from_bytes(export_table[0x24:0x28], "little")

    debug(f"Functions: {num_funcs}, Names: {num_names}")
    debug(f"AddrFuncsRVA: 0x{addr_funcs_rva:X}, AddrNamesRVA: 0x{addr_names_rva:X}, AddrOrdinalsRVA: 0x{addr_ordinals_rva:X}")

    func_array = mod_base + addr_funcs_rva
    name_array = mod_base + addr_names_rva
    ord_array = mod_base + addr_ordinals_rva

    for i in range(min(num_names, 4096)):
        name_ptr_pos = name_array + i * 4
        name_ptr_data = read_remote_memory(proc_handle, name_ptr_pos, 4)
        if not name_ptr_data:
            warn(f"Failed to read name pointer at index {i}")
            continue

        name_rva = int.from_bytes(name_ptr_data, "little")
        if name_rva == 0:
            continue

        export_name = read_remote_string(proc_handle, mod_base + name_rva)
        if not export_name:
            continue

        if export_name.lower() == func_name.lower():
            debug(f"Match found: '{export_name}'")

            ord_pos = ord_array + i * 2
            ord_data = read_remote_memory(proc_handle, ord_pos, 2)
            if not ord_data:
                error("Failed to read function ordinal")
                return 0

            ordinal = int.from_bytes(ord_data, "little")
            func_pos = func_array + ordinal * 4
            func_data = read_remote_memory(proc_handle, func_pos, 4)
            if not func_data:
                error("Failed to read function address")
                return 0

            func_rva = int.from_bytes(func_data, "little")
            final_addr = mod_base + func_rva
            debug(f"Resolved address for '{export_name}': 0x{final_addr:X}")
            return final_addr

    error(f"Function '{func_name}' not found in export table")
    return 0