import cv2
import mss
import numpy as np
import time

# 设置屏幕区域
screen_width, screen_height = 1920, 1080
crop_width, crop_height = 416,416
crop_x = (screen_width - crop_width) // 2
crop_y = (screen_height - crop_height) // 2

# 创建 MSS 连接
with mss.mss() as sct:
    # 设置捕捉参数
    monitor = {"top": crop_y, "left": crop_x, "width": crop_width, "height": crop_height}

    while True:
        # 记录开始时间
        start_time = time.time()
        a=time.time()
        # 获取屏幕截图
        img = np.array(sct.grab(monitor))

        # 将 BGR 图像转换为 RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        print((time.time()-a)*1000)
        # 显示图像
        cv2.imshow("Screen", img_rgb)

        # 计算延迟时间
        delay = max(1, int(10 - (time.time() - start_time) * 1000))

        # 检测按键，按下 ESC 键退出循环
        if cv2.waitKey(delay) == 27:
            break

# 关闭窗口
cv2.destroyAllWindows()


# import time
#
# import pygetwindow as gw
# from PIL import ImageGrab
# import numpy as np
# import cv2
#
# def get_screen_center_capture():
#     # 获取当前活动窗口
#     active_window = gw.getActiveWindow()
#
#     left, top, width, height = active_window.left, active_window.top, active_window.width, active_window.height
#
#     # 获取屏幕中心的 416x416 区域
#     left_center = (width - 416) // 2
#     top_center = (height - 416) // 2
#     right_center = left_center + 416
#     bottom_center = top_center + 416
#
#     # 不断循环进行屏幕截取
#     while True:
#         a=time.time()
#         # 获取屏幕截图
#         screenshot = ImageGrab.grab(bbox=(left + left_center, top + top_center, left + right_center, top + bottom_center))
#
#         # 将截图转换为numpy数组
#         img = np.array(screenshot)
#         # 将BGR格式转换为RGB格式
#         img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         print((time.time()-a)*1000)
#         # 在这里处理截取的屏幕图像，例如可以将图像传递给机器学习模型进行处理
#
#         # 在 OpenCV 窗口中显示实时截取的图像
#         cv2.imshow("Screen Center Capture", img_rgb)
#
#         # 检查是否按下 'q' 键，按下即退出循环
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#
#     # 关闭 OpenCV 窗口
#     cv2.destroyAllWindows()
#
# if __name__ == "__main__":
#     get_screen_center_capture()
