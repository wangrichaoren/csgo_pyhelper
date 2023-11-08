import sys
import os

current_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_path)
grandparent_directory = os.path.dirname(parent_directory)
sys.path.append(grandparent_directory)

import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QSizePolicy, QSpacerItem, QLabel
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from mainWindow import Ui_MainWindow
from tools import *
from pyqt_detector import Detector
from pyqt_screen_capture import ScreenCaptureThread
from pyqt_mouse_mover import MouseMover
import time
from threading import Thread
from pynput.mouse import Listener
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import random
import keyboard


class MyMainForm(QMainWindow, Ui_MainWindow):
    clear_view_signal = pyqtSignal()
    log_out_signal = pyqtSignal(int, str)
    test_det_sign = pyqtSignal(bool)
    start_game_sign = pyqtSignal(bool)
    det_res_show_sign = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)

        self.initParam()

        # 设置一些ui相关参数
        self.uiSetting()

        # 设置鼠标监听 键盘监听
        self.listening()

        # 初始化鼠标
        try:
            self.mover = MouseMover()
        except Exception as e:
            showMessageBox(self, "鼠标启动错误", e)
            exit(-1)

        # 加载检测者
        try:
            self.detector = Detector()
        except Exception as e:
            showMessageBox(self, "模型加载错误", e)
            exit(-1)

        # 加载屏幕捕获者
        try:
            self.screen_capturer_thread = ScreenCaptureThread()
        except Exception as e:
            showMessageBox(self, "捕获加载错误", e)
            exit(-1)
        self.screen_capturer_thread.start()

        # 连接所有信号与槽
        self.connect_sign_slot()

    def on_mouse_trigger(self, x, y, button, pressed):
        if pressed and button == button.x2:
            self.log_out_signal.emit(0, "切换敌人 - 警察")
            audio_source = "../datas/sound/c.mp3"
            media_content = QMediaContent(QUrl.fromLocalFile(audio_source))
            self.sound_player.setMedia(media_content)
            self.sound_player.play()
            self.cRadioButton.click()
        elif pressed and button == button.x1:
            self.log_out_signal.emit(0, "切换敌人 - 匪徒")
            audio_source = "../datas/sound/t.mp3"
            media_content = QMediaContent(QUrl.fromLocalFile(audio_source))
            self.sound_player.setMedia(media_content)
            self.sound_player.play()
            self.tRadioButton.click()
        elif pressed and button == button.middle:
            if not self.is_game_running:
                return
            self.is_pause = not self.is_pause
            if self.is_pause:
                self.log_out_signal.emit(0, "程序暂停")
                audio_source = "../datas/sound/pause.mp3"
                media_content = QMediaContent(QUrl.fromLocalFile(audio_source))
                self.sound_player.setMedia(media_content)
                self.sound_player.play()
                self.tRadioButton.click()
            else:
                self.log_out_signal.emit(0, "程序继续")
                audio_source = "../datas/sound/continue.mp3"
                media_content = QMediaContent(QUrl.fromLocalFile(audio_source))
                self.sound_player.setMedia(media_content)
                self.sound_player.play()

    def mouse_listen_thread(self):
        with Listener(on_click=self.on_mouse_trigger) as listener:
            listener.join()

    def on_key(self, event):
        if event.name == "caps lock":
            self.cap_idx += 1
            if self.cap_idx > 2:
                self.cap_idx = 0
            if self.cap_idx == 0:
                self.randowAtkBtn.setChecked(True)
                audio_source = "../datas/sound/random.mp3"
                media_content = QMediaContent(QUrl.fromLocalFile(audio_source))
                self.sound_player.setMedia(media_content)
                self.sound_player.play()
                return
            if self.cap_idx == 1:
                self.headAtkBtn.setChecked(True)
                audio_source = "../datas/sound/head.mp3"
                media_content = QMediaContent(QUrl.fromLocalFile(audio_source))
                self.sound_player.setMedia(media_content)
                self.sound_player.play()
                return
            if self.cap_idx == 2:
                self.bodyAtkBtn.setChecked(True)
                audio_source = "../datas/sound/body.mp3"
                media_content = QMediaContent(QUrl.fromLocalFile(audio_source))
                self.sound_player.setMedia(media_content)
                self.sound_player.play()
                return

    def listening(self):
        t = Thread(target=self.mouse_listen_thread)
        t.setDaemon(True)
        t.start()
        keyboard.on_press(self.on_key)
        self.log_out_signal.emit(0, "监听者创建")

    def connect_sign_slot(self):
        # 清空view
        self.clear_view_signal.connect(self.clearView)

        # 调试鼠标
        self.test_mouse_btn.clicked.connect(self.test_mouse_move)

        # 调试捕获屏幕
        self.test_capture_btn.clicked.connect(self.test_capture_screen)

        # 调试检测
        self.test_det_btn.clicked.connect(self.test_det_slot)

        # View 显示
        self.screen_capturer_thread.screen_shot_signal.connect(self.ViewShow, type=Qt.QueuedConnection)

        # 日志
        self.log_out_signal.connect(self.log_out_slot, type=Qt.QueuedConnection)

        self.test_det_sign.connect(self.detector.test_det_slot)

        # 调试检测图像传输
        self.detector.test_det_res_sign.connect(self.ViewShow, type=Qt.QueuedConnection)

        self.detector.det_log_out_sign.connect(self.log_out_slot)

        self.detector.test_det_ok.connect(self.test_det_ok_slot)

        self.mover.test_move_ok.connect(self.test_move_ok_slot)

        self.mover.mover_log_out_sign.connect(self.log_out_slot)

        self.screen_capturer_thread.screen_log_out_sign.connect(self.log_out_slot)

        self.lineEdit.textChanged.connect(self.score_le_change)

        # 打开
        self.start_btn.clicked.connect(self.start_game_slot)

        self.start_game_sign.connect(self.star_running)

        self.open_show_det_btn.clicked.connect(self.show_det_slot)

        self.det_res_show_sign.connect(self.ViewShow, type=Qt.QueuedConnection)

        self.randowAtkBtn.clicked.connect(self.click_random)

        self.headAtkBtn.clicked.connect(self.click_head)

        self.bodyAtkBtn.clicked.connect(self.click_body)

    def click_random(self):
        self.cap_idx = 0

    def click_head(self):
        self.cap_idx = 1

    def click_body(self):
        self.cap_idx = 2

    def show_det_slot(self):
        if not self.is_start_game:
            return
        self.is_show_det_res = not self.is_show_det_res
        if self.is_show_det_res:
            self.log_out_signal.emit(0, "开始实况")
            self.open_show_det_btn.setText("停止实况")
            self.open_show_det_btn.setStyleSheet("background-color: darkred; color: white;")
        else:
            self.log_out_signal.emit(0, "停止实况")
            self.open_show_det_btn.setText("开始实况")
            self.open_show_det_btn.setStyleSheet("")
            self.clear_view_signal.emit()

    def on_game_running(self, score):
        while True:
            if not self.is_game_running:
                return
            if self.is_pause:
                time.sleep(0.05)
                continue
            # st = time.time()
            frame = self.screen_capturer_thread.grab()
            is_c = 0
            if self.tRadioButton.isChecked():
                is_c = 1
            position_res, det_res_image = self.detector.detect2(frame, is_c, score)
            if self.is_show_det_res:
                self.det_res_show_sign.emit(det_res_image)
            if len(position_res) == 4:
                try:
                    # tt = time.time()
                    x1 = position_res[0]
                    y1 = position_res[1]
                    x2 = position_res[2]
                    y2 = position_res[3]
                    dif_x = (1920 - 416) / 2
                    dif_y = (1080 - 416) / 2
                    if self.randowAtkBtn.isChecked():
                        # 随机一个数
                        random_number = random.choice([5, 6, 7])
                        mid_xy = (
                            int(dif_x + int(x1 + int((x2 - x1) / 2))),
                            int(dif_y + int(y1 + int((y2 - y1) / random_number))))
                    elif self.headAtkBtn.isChecked():
                        mid_xy = (
                            int(dif_x + int(x1 + int((x2 - x1) / 2))),
                            int(dif_y + int(y1 + int((y2 - y1) / 7))))
                    else:
                        mid_xy = (
                            int(dif_x + int(x1 + int((x2 - x1) / 2))),
                            int(dif_y + int(y1 + int((y2 - y1) / 4))))

                    target_x, target_y = mid_xy[0], mid_xy[1]  # 这是屏幕像素坐标
                    self.mover.mouse_move(target_x, target_y)
                    # self.mover.mouse_down()
                    # self.mover.mouse_up()
                    # self.log_out_signal.emit(0,
#                          "检测到敌人后鼠标移动到敌人耗时 {} ms".format((time.time() - tt) * 1000))
                except Exception as e:
                    self.log_out_signal.emit(1, str(e))
                    continue
            # self.log_out_signal.emit(0, "完成一帧总耗时 {} ms".format((time.time() - st) * 1000))

    def star_running(self, flag):
        if flag:
            self.is_game_running = True
            t = Thread(target=self.on_game_running, args=(float(self.lineEdit.text()),))
            t.setDaemon(True)
            t.start()
        else:
            self.is_game_running = False

    def score_le_change(self):
        try:
            c = float(self.lineEdit.text())
        except Exception as e:
            self.lineEdit.setText("0.5")
            return
        if c < 0:
            self.lineEdit.setText("0.0")
        if c > 1.0:
            self.lineEdit.setText("1.0")

    def start_game_slot(self):
        if self.is_test_capture:
            showMessageBox(self, "调试捕获进行中", "调试捕获进行中,请关闭后在开启")
            return
        if self.is_test_det:
            showMessageBox(self, "调试检测进行中", "调试检测进行中,请关闭后在开启")
            return
        self.is_start_game = not self.is_start_game
        if self.is_start_game:
            self.log_out_signal.emit(0, "开始程序")
            self.start_btn.setText("停止程序")
            self.start_btn.setStyleSheet("background-color: darkred; color: white;")
            self.groupBox_2.setEnabled(False)
            self.tab_2.setEnabled(False)
            self.start_game_sign.emit(True)

        else:
            self.log_out_signal.emit(0, "停止程序")
            self.start_btn.setText("开始程序")
            self.start_btn.setStyleSheet("")
            self.groupBox_2.setEnabled(True)
            self.tab_2.setEnabled(True)
            self.start_game_sign.emit(False)
            self.clear_view_signal.emit()

    def test_move_ok_slot(self):
        showMessageBox(self, "调试鼠标完成", "调试鼠标完成")

    def test_det_ok_slot(self):
        self.test_det_btn.click()
        showMessageBox(self, "调试检测完成", "调试检测完成")
        self.clearView()

    def log_out_slot(self, level, msg):
        if level == 0:
            html = '<font color="black">[INFO] [{}]: {}</font>'.format(get_current_datetime(), msg)
        elif level == 1:
            html = '<font color="orange">[WARN] [{}]: {}</font>'.format(get_current_datetime(), msg)
        else:
            html = '<font color="red">[ERROR] [{}]: {}</font>'.format(get_current_datetime(), msg)

        self.plainTextEdit.appendHtml(html)

    def test_det_slot(self):
        self.is_test_det = not self.is_test_det
        if self.is_test_det:
            if self.is_test_capture:
                showMessageBox(self, "运行错误", "请先停止调试捕获,在开启调试检测!")
                self.is_test_det = not self.is_test_det
                return
            self.log_out_signal.emit(0, "开始调试检测")
            self.test_det_btn.setText("停止调试检测")
            self.test_det_btn.setStyleSheet("background-color: darkred; color: white;")
            self.test_det_sign.emit(True)
        else:
            self.log_out_signal.emit(0, "停止调试检测")
            self.test_det_btn.setText("调试检测")
            self.test_det_btn.setStyleSheet("")
            self.test_det_sign.emit(False)

    def ViewShow(self, cv_image):
        # 转换为QImage格式
        height, width, channel = cv_image.shape
        bytes_per_line = 3 * width
        qimage = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_BGR888)
        # 更新QGraphicsPixmapItem
        pixmap = QPixmap.fromImage(qimage)
        self.show_label.setPixmap(pixmap)

        # 要在这里clear掉才能清空
        # if not self.is_test_capture:
        #     self.clear_view_signal.emit()

    def initParam(self):
        self.is_test_capture = False
        self.is_test_det = False
        self.is_start_game = False
        self.is_game_running = False
        self.is_show_det_res = False
        self.is_pause = False
        self.cap_idx = 0

    def test_capture_screen(self):
        self.is_test_capture = not self.is_test_capture
        if self.is_test_capture:
            self.log_out_signal.emit(0, "开始调试采集")
            self.test_capture_btn.setText("停止调试采集")
            self.test_capture_btn.setStyleSheet("background-color: darkred; color: white;")
            self.screen_capturer_thread.test_screen_signal.emit(True)
        else:
            self.log_out_signal.emit(0, "停止调试采集")
            self.test_capture_btn.setText("调试采集")
            self.test_capture_btn.setStyleSheet("")
            self.screen_capturer_thread.test_screen_signal.emit(False)

    def clearView(self):
        self.show_label.setPixmap(QPixmap(""))

    def uiSetting(self):
        self.setFixedWidth(700)
        self.setFixedHeight(650)
        self.setWindowIcon(QIcon("../datas/icon/icon.png"))

        # 中间显示
        self.show_label.setAlignment(Qt.AlignCenter)

        # 设置窗口置顶标志
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.sound_player = QMediaPlayer()

        self.groupBox.setToolTip("快捷键 鼠标侧键 上（警察阵营） 下（匪徒阵营）")
        self.groupBox_3.setToolTip("快捷键 大写键 分别切换 随机/头/身体")
        self.groupBox_2.setToolTip(
            "检测目标 阈值 值调大会减少误检测 但可能会丢失目标；调小 会造成误检测。一般默认0.6即可。")

        # todo 随版本改变
        info_label = QLabel("版本号: v0.0.1 内部测试用")
        self.statusbar.addWidget(info_label)

    def test_mouse_move(self):
        self.log_out_signal.emit(0, "开始调试鼠标")
        self.mover.test_mover.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.show()
    sys.exit(app.exec_())
