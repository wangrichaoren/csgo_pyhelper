import ctypes
import time

PUL = ctypes.POINTER(ctypes.c_ulong)
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000

SendInput = ctypes.windll.user32.SendInput


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


def position(x=None, y=None):
    cursor = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
    return (x if x else cursor.x, y if y else cursor.y)


def size():
    return (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))


def _to_windows_coordinates(x=0, y=0):
    display_width, display_height = size()
    # the +1 here prevents exactly mouse movements from sometimes ending up off by 1 pixel
    windows_x = (x * 65536) // display_width + 1
    windows_y = (y * 65536) // display_height + 1
    return windows_x, windows_y


def moveTo(x=None, y=None):
    x, y = position(x, y)  # if only x or y is provided, will keep the current position for the other axis
    x, y = _to_windows_coordinates(x, y)
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(x, y, 0, (MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE), 0, ctypes.pointer(extra))
    command = Input(ctypes.c_ulong(0), ii_)
    SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


if __name__ == '__main__':
    a = time.time()
    x, y = position()
    xOffset, yOffset = 100, 100
    moveTo(x + xOffset, y + yOffset)
    print(time.time() - a)
