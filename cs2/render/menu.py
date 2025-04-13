import ctypes
from cs2.logger import debug
from cs2.render import primitives

menu_open = False

VK_INSERT = 0x2D
GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState

def toggle_menu():
    global menu_open
    state = GetAsyncKeyState(VK_INSERT)
    debug(f"[Menu] VK_INSERT key state: {state}")
    
    if state & 1:
        menu_open = not menu_open
        debug(f"[Menu] Toggled state: {'ON' if menu_open else 'OFF'}")

def draw_menu():
    debug("[Menu] draw_menu() called")
    toggle_menu()

    if not menu_open:
        debug("[Menu] Menu is closed – nothing drawn.")
        return

    primitives.CLEAR_COLOR = (0.0, 0.2, 0.6, 1.0)
    debug("[Menu] Menu is open – updated CLEAR_COLOR to blue tint.")