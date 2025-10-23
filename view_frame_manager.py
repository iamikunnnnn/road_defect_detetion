# frame_jump_manager.py
import cv2
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

class FrameJumpManager:
    def __init__(self, main_window):
        """
        初始化帧跳转管理器（复用主程序资源）
        :param main_window: 主程序窗口实例（用于获取主程序的视频资源和UI组件）
        """
        self.main_window = main_window  # 主程序窗口引用


        self.cap = main_window.result_cap  # 主程序的视频捕获对象（cv2.VideoCapture）
        self.frame_label = main_window.screen  # 主程序显示视频的QLabel
        self.table = main_window.frame_choose  # 主程序的缺陷表格（QTableView/Widget）

        # 内部状态（当前帧号，从主程序同步）
        self.current_frame = 0

        # 绑定信号槽
        self._bind_signals()

    def _bind_signals(self):
        """绑定表格和按钮的信号到跳转逻辑"""
        self.table.clicked.connect(self.on_table_clicked)  # 表格点击

    def on_table_clicked(self, index):
        """表格行点击：解析帧号并跳转到该帧"""

        print(3)
        row = index.row()
        # 从表格中获取帧号（根据你的表格列索引修改！假设第2列是帧号）
        # 若用QTableWidget：frame_num = int(self.table.item(row, 1).text())
        frame_num = int(self.table.model().item(row, 1).text())
        self.jump_to_frame(frame_num)

    def jump_to_frame(self, frame_num):
        """跳转到指定帧（核心方法，复用主程序的cap）"""
        # 校验帧号有效性（主程序可能已有总帧数属性，直接复用）
        # 检测 self.cap 是否有效
        if self.cap is None:
            print("错误：self.cap 未初始化（为 None）")
        elif not self.cap.isOpened():
            print("错误：self.cap 已创建，但视频未打开（可能文件路径错误或文件损坏）")
        else:
            print(3)
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(total_frames)
            print(total_frames)
            if frame_num < 0 or frame_num >= total_frames:
                return

            # 跳转到目标帧（通过主程序的cap操作）
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame_num  # 更新当前帧号
                self._update_label_with_frame(frame)  # 在主程序的Label上显示


    def _update_label_with_frame(self, frame):
        """将帧显示到主程序的QLabel上（复用主程序的显示逻辑）"""

        # BGR 转 RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = rgb.shape
        bytes_per_line = c * w

        # 创建 QImage 并显示
        image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.frame_label.setPixmap(QPixmap.fromImage(image))
        self.frame_label.setScaledContents(True)