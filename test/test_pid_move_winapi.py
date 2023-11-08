import time
import pyautogui


def move_mouse_smoothly_to_b(end_x, end_y, duration=0.01):
    # 获取当前鼠标位置
    start_x, start_y = pyautogui.position()

    # 计算每次移动的步长和移动总次数
    distance_x = end_x - start_x
    distance_y = end_y - start_y
    total_steps = int(max(abs(distance_x), abs(distance_y)))

    # 计算每次移动的步长
    step_x = distance_x / total_steps if total_steps > 0 else 0
    step_y = distance_y / total_steps if total_steps > 0 else 0

    # 控制鼠标移动，直到到达目标点
    for i in range(total_steps):
        current_x = start_x + i * step_x
        current_y = start_y + i * step_y
        pyautogui.moveTo(current_x, current_y, duration=0)  # 使用 pyautogui 控制鼠标移动

        # 计算下一步移动的时间
        time_per_step = duration / total_steps if total_steps > 0 else 0

        # 等待下一步移动
        time.sleep(time_per_step)

    # 最后一步移动到目标点
    pyautogui.moveTo(end_x, end_y, duration=0)


if __name__ == "__main__":
    # 设置目标点坐标
    end_x, end_y = 100, 100
    # pyautogui.moveTo(end_x, end_y, duration=0)
    a = time.time()
    pyautogui.moveRel(100, 100)
    print(time.time() - a)
    # # 设置规定时间，单位为秒
    # duration = 0.01
    #
    # # 调用函数进行平滑移动
    # move_mouse_smoothly_to_b(end_x, end_y, duration)
