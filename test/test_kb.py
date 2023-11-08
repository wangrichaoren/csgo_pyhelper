import keyboard


def on_key(event):
    if event.name == '0':  # 监听按下键盘上的 'a' 键
        print("Key 'a' is pressed")


keyboard.on_press(on_key)  # 监听按键事件

keyboard.wait('esc')  # 监听 'esc' 键，直到按下 'esc' 键退出程序
