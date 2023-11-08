import os
import tkinter as tk
from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np
import time

lib_path = os.path.abspath('./DXGI.pyd')
os.getcwd()
os.add_dll_directory(lib_path)
from ctypes import windll

windll.winmm.timeBeginPeriod(1)
stop = windll.kernel32.Sleep
import DXGI  # 把DXGI.pyd 复制到当前路径


class ScreenCaptureThread(QThread):
    # 传图信号
    screen_shot_signal = pyqtSignal(np.ndarray)
    test_screen_signal = pyqtSignal(bool)
    screen_log_out_sign = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self._is_show = False
        # 当前分辨率
        width, height = self._get_screen_resolution()

        # 原比例
        self.refer_width = 1920
        self.refer_height = 1080
        self.refer_region_width = 416
        self.refer_region_height = 416

        rw = width / self.refer_width
        rh = height / self.refer_height

        x1, y1, x2, y2 = self._get_center_coordinates(int(width), int(height), int(self.refer_region_width * rw),
                                                      int(self.refer_region_height * rh))

        self.graber = DXGI.capture(int(x1), int(y1), int(x2), int(y2))  # 屏幕左上角 到 右下角  （x1, y1 ,x2 ,y2)

        self.test_screen_signal.connect(self.test_screen_slot)

    def test_screen_slot(self, f):
        self._is_show = f

    def _get_center_coordinates(self, image_width, image_height, region_width, region_height):
        x1 = (image_width - region_width) // 2
        y1 = (image_height - region_height) // 2
        x2 = x1 + region_width
        y2 = y1 + region_height
        return x1, y1, x2, y2

    def _get_screen_resolution(self):
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height

    def grab(self):
        screen_shot_array = self.graber.cap()
        screen_shot_array = np.array(screen_shot_array)
        screen_shot_array = cv2.cvtColor(screen_shot_array, cv2.COLOR_BGRA2BGR)
        return screen_shot_array

    def run(self):
        while True:
            if not self._is_show:
                time.sleep(0.01)
                continue
            st = time.time()
            screen_shot_array = self.graber.cap()
            screen_shot_array = np.array(screen_shot_array)
            screen_shot_array = cv2.cvtColor(screen_shot_array, cv2.COLOR_BGRA2BGR)
            self.screen_log_out_sign.emit(0, "*-调试采集-* 采集一帧耗时 {} ms".format((time.time() - st) * 1000))
            # 发送出去
            self.screen_shot_signal.emit(screen_shot_array)
