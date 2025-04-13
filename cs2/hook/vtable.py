import ctypes
from cs2.hook.interfaces import create_dummy_device, get_swapchain
from cs2.logger import debug, error, success

_vtable_cache = {}

def get_present_vtable_index():
    index = 8
    debug(f"Using Present vtable index: {index}")
    return index

def fetch_swapchain_present():
    global _vtable_cache

    if "present" in _vtable_cache:
        cached = _vtable_cache["present"]
        debug(f"Returning cached Present address: 0x{cached:X}")
        return cached

    debug("Fetching Present address from dummy swapchain...")
    dummy_swapchain = create_dummy_device()

    if not dummy_swapchain:
        error("Failed to create dummy device for vtable fetch (null dummy_swapchain)")
        return None

    try:
        swapchain_ptr = ctypes.cast(dummy_swapchain, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))
        vtable = swapchain_ptr[0]
    except Exception as e:
        error(f"Failed to cast dummy_swapchain to vtable pointer: {e}")
        return None

    present_index = get_present_vtable_index()

    try:
        present_ptr = vtable[present_index]
        debug(f"[Dummy] IDXGISwapChain::Present is at index {present_index} -> 0x{present_ptr:X}")
    except Exception as e:
        error(f"Failed to access vtable[{present_index}]: {e}")
        return None

    _vtable_cache["present"] = present_ptr
    return present_ptr