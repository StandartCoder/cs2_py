import ctypes
from cs2.logger import debug, error
from cs2.render import renderer

CLEAR_COLOR = (1.0, 0.0, 0.0, 1.0)

def draw_frame():
    if not renderer.device:
        debug("draw_frame(): No device set, skipping")
        return

    if not renderer.context:
        debug("draw_frame(): No context set, skipping")
        return

    if not renderer.rtv:
        debug("draw_frame(): No render target view (RTV) set, skipping")
        return

    debug("draw_frame(): Drawing with clear color")

    context = renderer.context
    rtv = renderer.rtv
    color = (ctypes.c_float * 4)(*CLEAR_COLOR)

    try:
        clear_fn = ctypes.CFUNCTYPE(
            None, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_float)
        )(vfunc(context, 50))

        omset_fn = ctypes.CFUNCTYPE(
            None, ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p
        )(vfunc(context, 33))

        rtv_array = (ctypes.c_void_p * 1)(rtv)
        debug("draw_frame(): Calling OMSetRenderTargets...")
        omset_fn(context, 1, rtv_array, None)

        debug(f"draw_frame(): Calling ClearRenderTargetView with color {CLEAR_COLOR}")
        clear_fn(context, rtv, color)

    except Exception as e:
        error(f"draw_frame(): Failed to draw frame: {e}")

def vfunc(obj_ptr, index):
    try:
        vtable = ctypes.cast(obj_ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        return vtable[index]
    except Exception as e:
        error(f"vfunc(): Failed to get vfunc index {index}: {e}")
        return None