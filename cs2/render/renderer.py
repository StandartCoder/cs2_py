import ctypes
import ctypes.wintypes as wintypes
from cs2.logger import debug, error, success
from ctypes import POINTER, c_void_p, byref

ctypes.wintypes.HRESULT = ctypes.c_long

device = None
context = None
rtv = None

def initialize_renderer(swapchain_ptr):
    global device, context, rtv

    if device and context and rtv:
        debug("Renderer already initialized, skipping.")
        return

    debug("Initializing renderer...")

    # SwapChain->GetDevice(__uuidof(ID3D11Device), &device)
    get_device = ctypes.CFUNCTYPE(
        wintypes.HRESULT, ctypes.c_void_p, ctypes.c_void_p, POINTER(c_void_p)
    )(vfunc(swapchain_ptr, 7))
    device_ptr = c_void_p()

    hr = get_device(swapchain_ptr, _IID_ID3D11Device(), byref(device_ptr))
    if hr != 0 or not device_ptr:
        return error(f"Failed to get ID3D11Device, HRESULT: {hr}")

    debug(f"Got device pointer: 0x{device_ptr.value:X}")
    device = device_ptr

    # Device->GetImmediateContext(&context)
    get_context_fn = ctypes.CFUNCTYPE(
        None, c_void_p, POINTER(c_void_p)
    )(vfunc(device, 40))
    context_ptr = c_void_p()
    get_context_fn(device, byref(context_ptr))

    if not context_ptr:
        return error("Failed to get DeviceContext")

    debug(f"Got context pointer: 0x{context_ptr.value:X}")
    context = context_ptr

    # SwapChain->GetBuffer(0, __uuidof(ID3D11Texture2D), &backbuffer)
    get_buffer_fn = ctypes.CFUNCTYPE(
        wintypes.HRESULT, c_void_p, wintypes.UINT, c_void_p, POINTER(c_void_p)
    )(vfunc(swapchain_ptr, 8))
    backbuffer = c_void_p()

    hr = get_buffer_fn(swapchain_ptr, 0, _IID_ID3D11Texture2D(), byref(backbuffer))
    if hr != 0 or not backbuffer:
        return error(f"Failed to get backbuffer, HRESULT: {hr}")

    debug(f"Got backbuffer: 0x{backbuffer.value:X}")

    # Device->CreateRenderTargetView(backbuffer, NULL, &rtv)
    create_rtv_fn = ctypes.CFUNCTYPE(
        wintypes.HRESULT, c_void_p, c_void_p, c_void_p, POINTER(c_void_p)
    )(vfunc(device, 7))

    rtv_ptr = c_void_p()
    hr = create_rtv_fn(device, backbuffer, None, byref(rtv_ptr))
    if hr != 0 or not rtv_ptr:
        return error(f"Failed to create RenderTargetView, HRESULT: {hr}")

    debug(f"Got RTV pointer: 0x{rtv_ptr.value:X}")
    rtv = rtv_ptr

    success("Renderer initialized successfully")

def vfunc(obj_ptr, index):
    vtable = ctypes.cast(obj_ptr, POINTER(POINTER(c_void_p))).contents
    return vtable[index]

def _IID_ID3D11Device():
    return ctypes.create_string_buffer(b'\xdb\x6d\xb9\x59\x6e\xfd\xd7\x47\xa4\x7f\xd5\x50\x6c\x24\x7e\x6f', 16)

def _IID_ID3D11Texture2D():
    return ctypes.create_string_buffer(b'\x6f\x15\x95\x48\xfc\x7c\x48\x4e\xa5\x8e\xd7\x43\xac\x7e\x7c\xde', 16)