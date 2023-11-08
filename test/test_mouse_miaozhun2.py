import ctypes
import win32api
import win32con
import time

# 定义鼠标移动速度
aim_speed = 0.1


def mouse_smooth_move(target_x, target_y, duration=0.1):
    # 获取当前鼠标位置
    current_x, current_y = win32api.GetCursorPos()

    # 计算在指定时间内每一步的移动距离
    steps = int(duration * 100)
    delta_x = (target_x - current_x) / steps
    delta_y = (target_y - current_y) / steps

    # 平滑移动鼠标
    for step in range(steps + 1):
        x = int(current_x + delta_x * step)
        y = int(current_y + delta_y * step)
        win32api.SetCursorPos((x, y))
        time.sleep(duration / steps)


# 使用示例
if __name__ == "__main__":
    # 给定当前屏幕中的某个坐标（x, y）
    x, y = 1920 / 2, 1080 / 2
    # 调用 mouse_smooth_move 函数，并传入 x、y 和 aim_speed 的值
    a = time.time()
    mouse_smooth_move(x, y, aim_speed)
    print(time.time() - a)
