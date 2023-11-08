from PyQt5.QtWidgets import QMessageBox
import datetime


def showMessageBox(parent, title, msg):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


def get_current_datetime():
    # 获取当前的日期和时间
    current_datetime = datetime.datetime.now()

    # 格式化为指定的字符串
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")

    return formatted_datetime
