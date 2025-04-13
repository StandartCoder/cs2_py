import ctypes
import ctypes.wintypes as wintypes
from cs2.hook.vtable import fetch_swapchain_present, get_present_vtable_index
from cs2.render import renderer, primitives, menu
from cs2.logger import debug, error, success

ctypes.wintypes.HRESULT = ctypes.c_long

original_present = None
present_hook_ptr = None
swapchain_leaked = False

PresentFnType = ctypes.WINFUNCTYPE(
    wintypes.HRESULT,
    ctypes.c_void_p,
    wintypes.UINT,
    wintypes.UINT
)

@PresentFnType
def present_hook(swapchain_ptr, sync_interval, flags):
    debug("present_hook() called – top of function")
    global swapchain_leaked, original_present
    ctypes.windll.user32.MessageBoxW(None, "HOOK CALLED!", "DEBUG", 0)

    try:
        if not swapchain_leaked:
            debug("Swapchain not leaked yet, leaking now...")
            from cs2.hook.interfaces import set_real_swapchain, get_vtable
            set_real_swapchain(swapchain_ptr)
            swapchain_leaked = True
            debug("Leaked real CS2 swapchain")

            vtable = get_vtable()
            debug(f"Got vtable: {vtable}")
            real_present_addr = vtable[get_present_vtable_index()]
            debug(f"Real Present function address: 0x{real_present_addr:X}")
            new_hook_ptr = ctypes.cast(present_hook, ctypes.c_void_p).value
            debug(f"New hook function pointer: 0x{new_hook_ptr:X}")

            old_protect = wintypes.DWORD()
            if ctypes.windll.kernel32.VirtualProtect(
                ctypes.c_void_p(real_present_addr),
                ctypes.sizeof(ctypes.c_void_p),
                0x40,
                ctypes.byref(old_protect)
            ):
                debug("Memory protection changed to RWX for real Present")

                original_ptr = ctypes.cast(real_present_addr, ctypes.POINTER(ctypes.c_void_p))
                original_present = PresentFnType(original_ptr.contents.value)
                debug(f"Stored original Present: 0x{original_ptr.contents.value:X}")

                original_ptr.contents = ctypes.c_void_p(new_hook_ptr)
                debug("Overwritten vtable pointer to our hook")

                ctypes.windll.kernel32.VirtualProtect(
                    ctypes.c_void_p(real_present_addr),
                    ctypes.sizeof(ctypes.c_void_p),
                    old_protect.value,
                    ctypes.byref(old_protect)
                )
                success(f"Rehooked to real Present at 0x{real_present_addr:X}")
                ctypes.windll.user32.MessageBoxW(None, f"Rehooked real Present at 0x{real_present_addr:X}", "Rehook", 0)
            else:
                error("Failed to rehook to real Present")
                ctypes.windll.user32.MessageBoxW(None, "Failed to rehook memory protection", "ERROR", 0)

            return original_present(swapchain_ptr, sync_interval, flags)

        if renderer.device is None or renderer.context is None or renderer.rtv is None:
            debug("Calling renderer.initialize_renderer()")
            renderer.initialize_renderer(swapchain_ptr)


        debug("Calling menu.draw_menu()")
        menu.draw_menu()

        debug("Calling primitives.draw_frame()")
        primitives.draw_frame()

        ctypes.windll.user32.MessageBoxW(None, "PRESENT CALLED!", "HOOK", 0)

        return original_present(swapchain_ptr, sync_interval, flags)

    except Exception as e:
        error(f"Exception in present_hook: {e}")
        ctypes.windll.user32.MessageBoxW(None, f"Exception in hook:\n{str(e)}", "HOOK ERROR", 0)
        return 0

def initialize_hook():
    global original_present, present_hook_ptr

    debug("initialize_hook() called")
    debug("Fetching dummy Present address...")
    present_addr = fetch_swapchain_present()

    if not present_addr:
        error("Failed to fetch Present vtable address")
        return

    debug(f"Initial dummy Present address: 0x{present_addr:X}")
    present_hook_ptr = ctypes.cast(present_hook, ctypes.c_void_p).value
    debug(f"Hook function pointer: 0x{present_hook_ptr:X}")

    old_protect = wintypes.DWORD()
    if ctypes.windll.kernel32.VirtualProtect(
        ctypes.c_void_p(present_addr),
        ctypes.sizeof(ctypes.c_void_p),
        0x40,
        ctypes.byref(old_protect)
    ):
        debug("Memory protection changed to RWX for dummy Present")

        original_ptr = ctypes.cast(present_addr, ctypes.POINTER(ctypes.c_void_p))
        original_present = PresentFnType(original_ptr.contents.value)
        debug(f"Stored dummy Present: 0x{original_ptr.contents.value:X}")

        original_ptr.contents = ctypes.c_void_p(present_hook_ptr)
        debug("Overwritten vtable pointer to hook (dummy)")

        ctypes.windll.kernel32.VirtualProtect(
            ctypes.c_void_p(present_addr),
            ctypes.sizeof(ctypes.c_void_p),
            old_protect.value,
            ctypes.byref(old_protect)
        )

        success(f"Initially hooked dummy Present at 0x{present_addr:X}")
    else:
        error("Failed to hook dummy Present")
        ctypes.windll.user32.MessageBoxW(None, "VirtualProtect for dummy hook failed", "INIT ERROR", 0)
        return
    
    try:
        debug("Triggering dummy Present to manually enter present_hook()")
        from cs2.hook.interfaces import get_swapchain
        dummy_swapchain = get_swapchain()
        dummy_swapchain_ptr = ctypes.cast(dummy_swapchain, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))
        dummy_vtable = dummy_swapchain_ptr[0]

        dummy_present_fn = ctypes.CFUNCTYPE(
            wintypes.HRESULT,
            ctypes.c_void_p,
            wintypes.UINT,
            wintypes.UINT
        )(dummy_vtable[8])

        result = dummy_present_fn(dummy_swapchain, 0, 0)
        debug(f"Manual Present call returned: {result}")
    except Exception as e:
        error(f"Exception while calling dummy Present: {e}")
        ctypes.windll.user32.MessageBoxW(None, f"Present Trigger Error:\n{str(e)}", "HOOK ERROR", 0)