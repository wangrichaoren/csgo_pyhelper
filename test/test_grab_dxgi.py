"""
window 端最快的获取实时屏幕方法
"""

import os
import time

os.getcwd()
os.add_dll_directory('C:\\Users\\12168\\Desktop\\csgo_pyhelper\\test\\DXGI.pyd')
from ctypes import windll
import cv2
import numpy as np

windll.winmm.timeBeginPeriod(1)
stop = windll.kernel32.Sleep
import cv2
# 把DXGI.pyd 复制到当前路径
import DXGI

# import torch
g = DXGI.capture(0, 0, 320, 320)  # 屏幕左上角 到 右下角  （x1, y1 ,x2 ,y2)

while True:
    current_time = time.time()
    img = g.cap()
    img = np.array(img)
    # # 将图片转 BGR
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    last_time = time.time()
    time_used = last_time - current_time
    print(time_used)
    current_time, last_time = 0, 0
    cv2.imshow('c', img)
    cv2.waitKey(1)
