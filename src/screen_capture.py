import os
import tkinter as tk

lib_path = os.path.abspath('./DXGI.pyd')
os.getcwd()
os.add_dll_directory(lib_path)
from ctypes import windll

windll.winmm.timeBeginPeriod(1)
stop = windll.kernel32.Sleep
import DXGI  # 把DXGI.pyd 复制到当前路径


class ScreenCapture(object):

    def __init__(self):
        width, height = self._get_screen_resolution()
        self.refer_width = 1920
        self.refer_height = 1080

        self.refer_region_width = 416
        self.refer_region_height = 416

        rw = width / self.refer_width
        rh = height / self.refer_height

        x1, y1, x2, y2 = self._get_center_coordinates(int(width), int(height), int(self.refer_region_width * rw),
                                                      int(self.refer_region_height * rh))

        self.graber = DXGI.capture(int(x1), int(y1), int(x2), int(y2))  # 屏幕左上角 到 右下角  （x1, y1 ,x2 ,y2)

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

    def get_screen(self):
        pass
