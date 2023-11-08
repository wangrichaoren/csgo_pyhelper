# from playsound import playsound
#
# # 指定音频文件路径
# audio_file = "C:\\Users\\12168\\Videos\\test_video2.mp4"
#
# # 播放音频
# playsound(audio_file
#
#
from pynput.mouse import Listener


def on_mouse_click(x, y, button, pressed):
    if pressed and button == button.x2:  # 假设x2是鼠标侧键
        print("鼠标侧键 [up] 被按下")
    elif pressed and button == button.x1:
        print("鼠标侧键 [down] 被按下")


# 创建鼠标监听器
with Listener(on_click=on_mouse_click) as listener:
    listener.join()
