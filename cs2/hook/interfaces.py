import ctypes
from ctypes import POINTER, byref, c_void_p, windll
import ctypes.wintypes as wintypes
from cs2.logger import logger, debug, error, success

IID_IDXGISwapChain = ctypes.create_string_buffer(b'\xa0\x36\r1\xe7\xd2\x0a\x4c\xaa\x04\x6b\x77\xe5\xb1\x90\x3b', 16)
IID_ID3D11Device = ctypes.create_string_buffer(b'\xdb\x6f\x6d\xdb\xac\x77\x4e\x88\x82\x53\x81\x9d\xf9\xbb\xf1\x40', 16)
IID_ID3D11DeviceContext = ctypes.create_string_buffer(b'\xc0\xbf\xa9\x6c\xe0\x89\x44\xfb\x8e\xaf\x26\xf8\x79\x61\x90\xda', 16)

swapchain_ptr = None
device_ptr = None
context_ptr = None
vtable = None

def initialize_interfaces():
    global swapchain_ptr, device_ptr, context_ptr, vtable

    logger.info("Initializing DXGI swapchain...")

    hwnd = windll.user32.FindWindowW(None, "Counter-Strike 2")
    debug(f"FindWindowW returned HWND: {hwnd}")
    if not hwnd:
        logger.error("Failed to get CS2 window.")
        return False

    class DXGI_MODE_DESC(ctypes.Structure):
        _fields_ = [
            ("Width", wintypes.UINT),
            ("Height", wintypes.UINT),
            ("RefreshRate", ctypes.c_byte * 8),
            ("Format", wintypes.UINT),
            ("ScanlineOrdering", wintypes.UINT),
            ("Scaling", wintypes.UINT),
        ]

    class DXGI_SAMPLE_DESC(ctypes.Structure):
        _fields_ = [
            ("Count", wintypes.UINT),
            ("Quality", wintypes.UINT),
        ]

    class DXGI_SWAP_CHAIN_DESC(ctypes.Structure):
        _fields_ = [
            ("BufferDesc", DXGI_MODE_DESC),
            ("SampleDesc", DXGI_SAMPLE_DESC),
            ("BufferUsage", wintypes.UINT),
            ("BufferCount", wintypes.UINT),
            ("OutputWindow", wintypes.HWND),
            ("Windowed", wintypes.BOOL),
            ("SwapEffect", wintypes.UINT),
            ("Flags", wintypes.UINT),
        ]

    swap_desc = DXGI_SWAP_CHAIN_DESC()
    swap_desc.BufferDesc.Width = 800
    swap_desc.BufferDesc.Height = 600
    swap_desc.BufferDesc.Format = 87  # DXGI_FORMAT_R8G8B8A8_UNORM
    swap_desc.SampleDesc.Count = 1
    swap_desc.SampleDesc.Quality = 0
    swap_desc.BufferUsage = 32  # DXGI_USAGE_RENDER_TARGET_OUTPUT
    swap_desc.BufferCount = 1
    swap_desc.OutputWindow = hwnd
    swap_desc.Windowed = True
    swap_desc.SwapEffect = 0  # DXGI_SWAP_EFFECT_DISCARD
    swap_desc.Flags = 0

    debug("DXGI_SWAP_CHAIN_DESC populated")

    try:
        d3d11 = ctypes.windll.LoadLibrary("d3d11.dll")
        D3D11CreateDeviceAndSwapChain = d3d11.D3D11CreateDeviceAndSwapChain
        D3D11CreateDeviceAndSwapChain.restype = ctypes.c_int
    except Exception as e:
        error(f"Failed to load d3d11.dll or get function: {e}")
        return False

    swapchain = c_void_p()
    device = c_void_p()
    context = c_void_p()

    debug("Calling D3D11CreateDeviceAndSwapChain...")

    result = D3D11CreateDeviceAndSwapChain(
        None, 1, None, 0, None, 0, 7,
        ctypes.byref(swap_desc),
        ctypes.byref(swapchain),
        ctypes.byref(device),
        None,
        ctypes.byref(context)
    )

    if result != 0:
        error(f"D3D11CreateDeviceAndSwapChain failed with HRESULT: {result}")
        return False

    debug("D3D11CreateDeviceAndSwapChain succeeded")

    swapchain_ptr = swapchain
    device_ptr = device
    context_ptr = context

    vtable = ctypes.cast(swapchain_ptr, POINTER(POINTER(c_void_p))).contents
    debug(f"Swapchain pointer: 0x{swapchain_ptr.value:X}")
    debug(f"Device pointer: 0x{device_ptr.value:X}")
    debug(f"Context pointer: 0x{context_ptr.value:X}")
    logger.info("Swapchain vtable acquired.")

    return True

def set_real_swapchain(ptr):
    global swapchain_ptr, vtable
    debug("Setting real swapchain from CS2")
    swapchain_ptr = ptr
    vtable = ctypes.cast(swapchain_ptr, POINTER(POINTER(c_void_p))).contents
    debug(f"Real swapchain set: 0x{swapchain_ptr.value:X}")

def get_swapchain():
    debug(f"Returning swapchain_ptr: {swapchain_ptr}")
    return swapchain_ptr

def get_vtable():
    debug(f"Returning vtable: {vtable}")
    return vtable

def create_dummy_device():
    debug("Creating dummy DXGI device...")
    if initialize_interfaces():
        debug("Dummy DXGI device created successfully.")
        return get_swapchain()
    error("Failed to create dummy DXGI device.")
    return None