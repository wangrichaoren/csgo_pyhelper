import ghub_mouse as ghub
import win32api
from PyQt5.QtCore import pyqtSignal, QThread
from threading import Thread
import time


class MouseMover(QThread):
    mover_log_out_sign = pyqtSignal(int, str)
    test_mover = pyqtSignal()
    test_move_ok = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.liner_step = 5
        self.liner_time = 0.001
        self.liner_step_time = self.liner_time / self.liner_step

        self.test_mover.connect(self.test_move)

    def mouse_move(self, screen_x, screen_y):
        cur_x, cur_y = win32api.GetCursorPos()
        ghub.mouse_xy(round(screen_x - cur_x), round(screen_y - cur_y))

    def mouse_move_liner(self, screen_x, screen_y):
        curx, cury = win32api.GetCursorPos()
        dis_thr = 50
        if abs(screen_x - curx) < dis_thr and abs(screen_y - cury) < dis_thr:
            ghub.mouse_xy(round(screen_x - curx), round(screen_y - cury))
            return
        dx = (screen_x - curx) / self.liner_step
        dy = (screen_y - cury) / self.liner_step
        for _ in range(self.liner_step):
            ghub.mouse_xy(round(dx), round(dy))
            time.sleep(self.liner_step_time)

    def mouse_down(self):
        ghub.mouse_down(2)
        ghub.mouse_down(1)

    def mouse_up(self):
        ghub.mouse_up(2)
        ghub.mouse_up(1)

    def test_move_work(self):
        for _ in range(50):
            self.mouse_move(10, 0)
            time.sleep(0.01)
        for _ in range(50):
            self.mouse_move(-10, 0)
            time.sleep(0.01)
        self.mover_log_out_sign.emit(0, "调试鼠标完成")
        self.test_move_ok.emit()

    def test_move(self):
        # 中心416*416区域画方框
        t = Thread(target=self.test_move_work)
        t.setDaemon(True)
        t.start()


if __name__ == '__main__':
    m = MouseMover()

    for i in range(32):
        m.moveRel(-10, 0)
