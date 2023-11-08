# import ctypes
#
# # 定义MOUSEEVENTF_MOVE、MOUSEEVENTF_ABSOLUTE和MOUSEEVENTF_VIRTUALDESK的值
# MOUSEEVENTF_MOVE = 0x0001
# MOUSEEVENTF_ABSOLUTE = 0x8000
# MOUSEEVENTF_VIRTUALDESK = 0x4000
# import time
#
# # 使用ctypes加载user32.dll库
# user32 = ctypes.WinDLL("user32.dll")
#
#
# # 定义mouse_event函数，用于模拟鼠标移动
# def mouse_move(dx, dy):
#     # 使用user32.dll库中的mouse_event函数发送模拟的鼠标移动事件
#     user32.mouse_event(MOUSEEVENTF_MOVE, dx, dy, 0, 0)
#
#
# # 使用示例
# if __name__ == "__main__":
#     # 在x和y方向上移动鼠标
#     a = time.time()
#     mouse_move(200, 200)
#     print((time.time() - a) * 1000)


# import ctypes
# import time
#
# # 定义MOUSEEVENTF_MOVE、MOUSEEVENTF_VIRTUALDESK的值
# MOUSEEVENTF_MOVE = 0x0001
# MOUSEEVENTF_VIRTUALDESK = 0x4000
#
# # 定义MOUSEINPUT结构体，用于模拟鼠标移动
# class MOUSEINPUT(ctypes.Structure):
#     _fields_ = [("dx", ctypes.c_long),
#                 ("dy", ctypes.c_long),
#                 ("mouseData", ctypes.c_ulong),
#                 ("dwFlags", ctypes.c_ulong),
#                 ("time", ctypes.c_ulong),
#                 ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
#
# # 定义INPUT结构体，用于模拟鼠标事件
# class INPUT(ctypes.Structure):
#     _fields_ = [("type", ctypes.c_ulong),
#                 ("mi", MOUSEINPUT)]
#
# # 定义INPUT结构体中type的值，表示输入类型为鼠标事件
# INPUT_MOUSE = 0
#
# # 使用ctypes加载user32.dll库
# user32 = ctypes.WinDLL("user32.dll")
#
# # 定义mouse_move_rel函数，用于模拟鼠标移动
# def mouse_move_rel(dx, dy):
#     # 创建一个MOUSEINPUT结构体对象，填充相关信息
#     mouse_input = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_VIRTUALDESK, 0, None)
#
#     # 创建一个INPUT结构体对象，填充相关信息
#     input_struct = INPUT(INPUT_MOUSE, mouse_input)
#
#     # 使用user32.dll库中的SendInput函数发送模拟的鼠标事件
#     user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
#
# # 使用示例
# if __name__ == "__main__":
#     # 在x和y方向上移动鼠标
#     for i in range(2):
#         a=time.time()
#         mouse_move_rel(100, 100)
#         print((time.time() - a) * 1000)


# import ctypes
# import time
#
# # 使用ctypes加载user32.dll库
# user32 = ctypes.windll.user32
#
#
# # 定义SetCursorPos函数，用于将鼠标位置移动到指定坐标
# def set_cursor_pos(x, y):
#     user32.SetCursorPos(x, y)
#
#
# # 使用示例
# if __name__ == "__main__":
#     # 将鼠标移动到屏幕坐标 (100, 100)
#     a = time.time()
#     set_cursor_pos(100, 100)
#     print((time.time() - a) * 1000)


