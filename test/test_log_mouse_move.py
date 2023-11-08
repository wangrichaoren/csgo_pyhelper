import win32api
import time
from cffi import FFI

# 定义鼠标移动速度
aim_speed = 0.1

ffi = FFI()
lib = ffi.dlopen("./libmouse.dll")

ffi.cdef(
    "BOOL mouse_open(void);"
    "void mouse_close(void);"
    "void mouse_move(unsigned char button, signed char x, signed char y, signed char wheel);"
)
if lib.mouse_open() == 1:
    print('mouse open.')

time_out = 0.05

current_x, current_y = win32api.GetCursorPos()
print(current_x, current_y)

# target 381 43
target_x = 381
target_y = 43
dx = target_x - current_x
dy = target_y - current_y
steps = 50
stepx = int(dx / steps)
stepy = int(dy / steps)
sleep_t = time_out / steps
if stepx == 0 and stepy == 0:
    for i in range(3):
        lib.mouse_move(0, int(dx/3), int(dy/3), 0)
        time.sleep(0.001)
    exit(0)
cx, cy = 0, 0
# 当stepx y=0的时候说明移动的距离很短，那么直接移动到那里
for step in range(steps):
    lib.mouse_move(0, stepx, stepy, 0)
    # cx += stepx
    # cy += stepy
    # if (abs(cx-))
    time.sleep(0.001)  # 这个时间不行

# lib.mouse_move(0, 120, 0, 0)

# def mouse_smooth_move(target_x, target_y, duration=0.01):
#     # 获取当前鼠标位置
#     current_x, current_y = win32api.GetCursorPos()
#
#     # 计算在指定时间内每一步的移动距离
#     steps = int(duration * 4)
#     delta_x = int((target_x - current_x) / steps)  # float 的问题
#     delta_y = int((target_y - current_y) / steps)
#
#     # 平滑移动鼠标
#     for step in range(steps + 1):
#         lib.mouse_move(0, delta_x, delta_y, 0)
#         # time.sleep(0.001)
#
#
# # 使用示例
# if __name__ == "__main__":
#     # 给定当前屏幕中的某个坐标（x, y）
#     x, y = 1920 / 2, 1080 / 2
#     # 调用 mouse_smooth_move 函数，并传入 x、y 和 aim_speed 的值
#     a = time.time()
#     mouse_smooth_move(x, y, aim_speed)
#     print(time.time() - a)
#     lib.mouse_close()
