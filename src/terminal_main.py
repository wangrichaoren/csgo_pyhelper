import os
import time
import cv2
import numpy as np
from detector import Detector
import keyboard
from pynput.mouse import Listener
from threading import Thread
import ctypes
from cffi import FFI
import win32api

"""
一些说明：
1.快捷键 [+] / [-] 分别控制是否开启检测 开 / 关
2.快捷键（鼠标侧键） 上 / 下 分别控制检测 警察 / 匪徒
3.DXGI 为目前最快速的屏幕截取手段 需要 [GPU] 支持
"""

lib_path = os.path.abspath('./DXGI.pyd')
os.getcwd()
os.add_dll_directory(lib_path)
from ctypes import windll

windll.winmm.timeBeginPeriod(1)
stop = windll.kernel32.Sleep
import DXGI  # 把DXGI.pyd 复制到当前路径


def get_center_coordinates(image_width, image_height, region_width, region_height):
    x1 = (image_width - region_width) // 2
    y1 = (image_height - region_height) // 2
    x2 = x1 + region_width
    y2 = y1 + region_height
    return x1, y1, x2, y2


image_width = 1920  # 分辨率1920*1080
image_height = 1080
region_width = 416  # 截取范围 中心416*416
region_height = 416

# 获取中心416*416的左上角 右下角 x1 y1 x2 y2
x1, y1, x2, y2 = get_center_coordinates(image_width, image_height, region_width, region_height)

g = DXGI.capture(x1, y1, x2, y2)  # 屏幕左上角 到 右下角  （x1, y1 ,x2 ,y2)

# logitech 鼠标dll加载
ffi = FFI()
mouse_dll_path = os.path.abspath('./libmouse.dll')
mouse = ffi.dlopen(mouse_dll_path)
ffi.cdef(
    "BOOL mouse_open(void);"
    "void mouse_close(void);"
    "void mouse_move(unsigned char button, signed char x, signed char y, signed char wheel);"
)
if mouse.mouse_open() == 1:
    print('mouse open.')

# 检测项
is_detect = True
is_detect_c = True  # 默认检测c（即警察）


def on_key(event):
    global is_detect
    if event.name == '+':
        print('helper开启')
        is_detect = True
    elif event.name == '-':
        is_detect = False
        print('helper关闭')


def on_mouse_click(x, y, button, pressed):
    global is_detect_c
    if pressed and button == button.x2:
        print("开启检测警察...")
        is_detect_c = True
    elif pressed and button == button.x1:
        print("开启检测匪徒...")
        is_detect_c = False


def size():
    return (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))


def mouse_listen_thread():
    with Listener(on_click=on_mouse_click) as listener:
        listener.join()


def _to_windows_coordinates(x=0, y=0):
    display_width, display_height = size()
    # the +1 here prevents exactly mouse movements from sometimes ending up off by 1 pixel
    windows_x = (x * 65536) // display_width + 1
    windows_y = (y * 65536) // display_height + 1
    return windows_x, windows_y


steps = 5
time_out = 0.03
sleep_t = time_out / steps


def main():
    global is_detect, is_detect_c
    keyboard.on_press(on_key)  # 监听按键事件

    t = Thread(target=mouse_listen_thread)  # 监听鼠标事件
    t.setDaemon(True)
    t.start()

    detector = Detector()

    while True:
        if not is_detect:
            time.sleep(0.01)
            continue
        # 获取屏幕截图
        img = g.cap()
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        position_res, det_res_image = detector.detect2(img, is_det_c=is_detect_c, score_thr=0.6)

        if len(position_res) == 4:
            try:
                # st = time.time()
                x1 = position_res[0]
                y1 = position_res[1]
                x2 = position_res[2]
                y2 = position_res[3]
                dif_x = (1920 - 416) / 2
                dif_y = (1080 - 416) / 2
                mid_xy = (int(dif_x + int(x1 + int((x2 - x1) / 2))), int(dif_y + int(y1 + int((y2 - y1) / 3))))
                target_x, target_y = mid_xy[0], mid_xy[1]  # 这是屏幕像素坐标
                current_x, current_y = win32api.GetCursorPos()
                dx = target_x - current_x
                dy = target_y - current_y
                stepx = int(dx / steps)
                stepy = int(dy / steps)
                if stepx == 0 and stepy == 0:
                    for i in range(2):
                        mouse.mouse_move(0, int(dx / 2), int(dy / 2), 0)
                        time.sleep(0.0001)
                else:
                    for step in range(steps):
                        mouse.mouse_move(0, stepx, stepy, 0)
                        time.sleep(sleep_t)
                # print((time.time() - st) * 1000)
            except Exception as e:
                continue


if __name__ == '__main__':
    main()
