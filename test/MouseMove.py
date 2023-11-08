import time
from simple_pid import PID
import ghub_mouse as ghub
import math


def mouse_move(rel_x, rel_y):
    ghub.mouse_xy(round(rel_x), round(rel_y))


if __name__ == "__main__":
    pidx = PID(1.1, 0.1, 0.1, setpoint=0, sample_time=0.001, )
    pidy = PID(1.1, 0.1, 0.1, setpoint=0, sample_time=0.001, )
    x = pidx(0)
    y = pidy(0)
    a = time.time()
    kkk = math.atan2(-500, 416) * 416
    x2 = pidx(kkk)
    y2 = pidy(kkk)
    print(x2)
    print(y2)
    mouse_move(x2, y2)
    print(time.time() - a)
    # import time
    # trials = 10000
    # start_time = time.time()
    # for i in range(trials):
    #     mouse_move(100,0)
    #     mouse_move(-100,0)
    # fps = trials/(time.time()-start_time)
    # print(time.time()-start_time)
    # print(fps)
