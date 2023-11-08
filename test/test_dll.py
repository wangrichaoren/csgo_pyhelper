# test_ffi.py
from cffi import FFI
import time

ffi = FFI()
lib = ffi.dlopen("./libmouse.dll")

ffi.cdef(
    "BOOL mouse_open(void);"
    "void mouse_close(void);"
    "void mouse_move(unsigned char button, signed char x, signed char y, signed char wheel);"
)

print(lib.mouse_open())

button = 0
x = 724
y = 0
wheel = 0
print(type(x))
for i in range(32):
    time.sleep(0.001)
    lib.mouse_move(button, x, y, wheel)  # 这是个movel

lib.mouse_close()
