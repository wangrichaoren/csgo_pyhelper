from cffi import FFI
import os


class MouseMover(object):
    def __init__(self):
        ffi = FFI()
        mouse_dll_path = os.path.abspath('./libmouse.dll')
        self.mouse = ffi.dlopen(mouse_dll_path)
        ffi.cdef(
            "BOOL mouse_open(void);"
            "void mouse_close(void);"
            "void mouse_move(unsigned char button, signed char x, signed char y, signed char wheel);"
        )

    def open(self) -> bool:
        if self.mouse.mouse_open() == 1:
            return True
        return False

    def close(self):
        self.mouse.mouse_close()

    def moveRel(self, x, y):
        self.mouse.mouse_move(0, x, y, 0)


if __name__ == '__main__':
    m = MouseMover()
    m.open()

    for i in range(32):
        m.moveRel(-10, 0)

    m.close()
