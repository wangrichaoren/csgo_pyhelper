import time
from cffi import FFI
import os
from simple_pid import PID

ffi = FFI()
mouse_dll_path = os.path.abspath('./libmouse.dll')
mouse = ffi.dlopen(mouse_dll_path)
ffi.cdef(
    "BOOL mouse_open(void);"
    "void mouse_close(void);"
    "void mouse_move(unsigned char button, signed char x, signed char y, signed char wheel);"
)
mouse.mouse_open()


def move_mouse_smoothly(end_x, end_y):
    # 设置 PID 控制参数
    Kp = 0.5
    Ki = 0.1
    Kd = 0.1
    pid_x = PID(Kp, Ki, Kd, setpoint=end_x)
    pid_y = PID(Kp, Ki, Kd, setpoint=end_y)

    current_x, current_y = 0, 0

    # 设置目标点
    target_x = end_x
    target_y = end_y

    # print(abs(current_x - target_x))

    # 控制鼠标移动，直到到达目标点
    while True:
        if abs(target_x - current_x) <= 2 and abs(target_y - current_y) <= 2:
            print('daowei1')
            break
        # 计算 PID 控制输出
        control_x = int(pid_x(current_x))
        control_y = int(pid_y(current_y))

        # 更新鼠标位置
        current_x += control_x
        current_y += control_y
        print(control_x)
        print(control_y)
        print('-------------')

        mouse.mouse_move(0, control_x, control_y, 0)

        # 添加适当的延迟，控制移动速度
        time.sleep(0.001)


if __name__ == "__main__":
    move_mouse_smoothly(50, 100)
