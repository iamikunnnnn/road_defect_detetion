import sys
import os

import pandas as pd
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel,
                             QFileDialog, QMessageBox, QProgressDialog,QTableView)
import torchvision
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QImage, QStandardItemModel, QStandardItem
from view_frame_manager import FrameJumpManager
import cv2
import torch
import numpy as np

from ultralytics import YOLO
import os
import sys
import json
import requests

# frame_jump_manager.py
import cv2
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import os





os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7000"

# 动态添加EXE所在目录到Python模块搜索路径
# （手动添加的analyze_gemini.py等文件在这里）
exe_dir = os.path.dirname(sys.executable)  # EXE所在目录
sys.path.append(exe_dir)  # 让Python能在这里搜索模块
from analyze_gemini import main
from view_frame_manager import FrameJumpManager
import sys, os

def resource_path(relative_path):
    """返回打包后可用的资源绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class myWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 检查 UI 文件是否存在
        if not os.path.exists('./UI.ui'):
            QMessageBox.critical(None, "错误", "UI文件 'UI.ui' 不存在")
            sys.exit(1)

        ui = uic.loadUi('./UI.ui', self)

        # 定义控件
        self.screen: QLabel = ui.scream
        self.btn_loadFile: QPushButton = ui.btn_load
        self.btn_detect: QPushButton = ui.btn_detect
        self.btn_get_results: QPushButton = ui.btn_get_results
        self.agent_text: QPushButton = ui.agent_text
        self.send2agent: QPushButton = ui.send2agent
        self.frame_choose: QTableView = ui.frame_choose

        # 连接信号槽
        self.btn_loadFile.clicked.connect(self.btn_loadFile_slot)
        self.btn_detect.clicked.connect(self.btn_detect_slot)
        self.btn_get_results.clicked.connect(self.btn_get_results_slot)
        # self.agent_text.clicked.connect(self.agent_text_slot)
        self.send2agent.clicked.connect(self.send2agent_slot)


        # 初始化变量
        self.current_file = None
        self.video_path = None
        self.cap = None
        self.timer_video = None
        self.model = None
        self.is_detecting = False  # 是否正在检测
        self.is_video = False  # 当前是否为视频

        # 加载 YOLOv5 模型
        self.load_model()

        self.object_sizes = []  # 格式：[(类别名称, 宽度, 高度), ...]


    def _get_result_tabel(self):
        # 固定xlsx路径
        excel_path = "result.xlsx"
        # 读取xlsx（默认读第一个工作表）
        df = pd.read_excel(excel_path)
        # 创建模型（行数=数据行数，列数=数据列数）
        model = QStandardItemModel(df.shape[0], df.shape[1])
        # 设置表头（用Excel的列名）
        model.setHorizontalHeaderLabels(df.columns.tolist())

        # 遍历数据填充模型
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                # 处理空值（NaN→空字符串）
                cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                # 创建单元格项并添加到模型
                model.setItem(row, col, QStandardItem(cell_value))

        self.frame_choose.setModel(model)

    def load_model(self):
        """加载 YOLOv5 模型"""
        try:
            # 检查权重文件
            if not os.path.exists('./yolov11m.engine'):
                QMessageBox.warning(self, "警告", "未找到模型权重\n检测功能将不可用")
                return

            print("正在加载 YOLOv11m 模型...")
            # 使用 torch.hub 加载本地模型
            self.model = YOLO("./yolov11m.engine")  # pretrained YOLO11n model

            print("模型加载成功!")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"模型加载失败:\n{str(e)}")
            self.model = None

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        self.cleanup_video()
        event.accept()

    def cleanup_video(self):
        """清理视频资源"""
        if self.timer_video and self.timer_video.isActive():
            self.timer_video.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

    def btn_loadFile_slot(self):
        """读取文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "./",
            "所有支持的文件 (*.mp4 *.avi *.jpg *.jpeg *.png);;视频 (*.mp4 *.avi);;图片 (*.jpg *.jpeg *.png)"
        )

        if not file_path:
            return

        # 清理之前的资源
        self.cleanup_video()
        self.is_detecting = False  # 重置检测状态

        self.current_file = file_path
        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".mp4", ".avi"]:
            print(f"加载视频文件: {file_path}")
            self.is_video = True
            self.video_path = file_path
            self.play_video(file_path)

        elif ext in [".jpg", ".jpeg", ".png"]:
            print(f"加载图片文件: {file_path}")
            self.is_video = False
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "警告", "无法加载图片文件")
                return
            self.screen.setPixmap(pixmap)
            self.screen.setScaledContents(True)
        else:
            QMessageBox.warning(self, "警告", "不支持的文件格式")

    def play_video(self, video_path):
        """播放视频"""
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            QMessageBox.warning(self, "警告", "无法打开视频文件")
            return


        # 初始化时间相关变量
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)  # 获取视频帧率
        self.fps = self.fps if self.fps > 0 else 30  # 异常处理
        self.frame_idx = 0  # 初始化帧索引（从0开始）

        # 3. 初始化视频写入器（保存处理后的视频）
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 编码格式：MP4推荐使用cv2.VideoWriter_fourcc(*'mp4v')，文件后缀为.mp4
        self.output_path = "processed_video.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(
            self.output_path,
            fourcc,
            self.fps,
            (self.frame_width, self.frame_height)  # 必须与帧分辨率一致
        )
        if not self.writer.isOpened():
            print("错误：无法创建输出视频文件")
            self.cap.release()
            sys.exit(1)

        # 创建定时器
        if not self.timer_video:
            self.timer_video = QTimer(self)
            self.timer_video.timeout.connect(self.next_frame)

        # 获取视频帧率并设置定时器间隔
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30  # 默认帧率
        interval = int(1000 / fps)

        print(f"视频帧率: {fps} FPS, 定时器间隔: {interval} ms")
        self.timer_video.start(interval)

    def next_frame(self):
        """更新视频帧"""
        if not self.cap:
            return

        ret, frame = self.cap.read()
        if not ret:
            # 视频播放结束，停止播放并释放资源
            # 1. 停止定时器，避免继续触发
            if self.timer_video and self.timer_video.isActive():
                self.timer_video.stop()
            # 2. 释放视频捕获资源
            self.cap.release()
            self.cap = None  # 置空，避免后续误操作
            # 3. 可选：提示视频结束
            QMessageBox.information(self, "提示", "视频已播放完毕")
            self.time_out = True

            # 释放writer来保证视频保存成功
            self.writer.release()

            return
        self.current_frame_num = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        # 计算当前帧的视频时间（秒）
        current_time_sec = self.frame_idx / self.fps
        # 转换为 "分:秒" 格式（如 1分23秒）
        minutes = int(current_time_sec // 60)
        seconds = int(current_time_sec % 60)
        self.time_str = f"{minutes}分{seconds}秒"

        # 如果正在检测模式,进行实时推理
        if self.is_detecting and self.model is not None:
            frame = self.detect_frame(frame)
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.writer.write(bgr_frame)
        # 显示帧
        self.display_frame(frame)
        self.frame_idx += 1  # 帧索引递增

    def detect_frame(self, frame):
        """对单帧进行跟踪（替代检测）并绘制结果，包含目标编号"""
        try:
            # 关键修改：将model(frame)改为model.track()，启用跟踪
            # results = self.model.track(
            #     frame,
            #     tracker="botsort.yaml",  # 指定跟踪器配置（默认提供，无需额外文件）
            #     persist=True  # 保持跟踪状态（跨帧关联目标，核心参数）
            # )
            results = self.model.predict(frame,conf=0.1,iou=0.3,device="cuda")

            # 渲染结果（自动显示目标ID，与原plot()用法一致）
            frame = results[0].plot()  # plot()会自动在框旁标注ID


            boxes = results[0].boxes

            for box in boxes:
                # # 新增：获取目标唯一ID（跟踪核心）
                # track_id = int(box.id.item())  # ID转为整数
                # 原有类别和大小计算逻辑保留
                cls_id = int(box.cls.item())
                cls_name = self.model.names[cls_id]
                xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                xmin, ymin, xmax, ymax = xyxy

                # 3. 计算中心点坐标（核心）
                center_x = round((xmin + xmax) / 2, 2)  # 中心点x = (xmin + xmax) / 2
                center_y = round((ymin + ymax) / 2, 2)  # 中心点y = (ymin + ymax) / 2
                # 存储信息
                self.object_sizes.append((
                    self.time_str,
                    # track_id,  # 新增：目标编号
                    self.current_frame_num,
                    cls_name,
                    round(center_x, 2),
                    round(center_y, 2)
                ))

            del results  # 释放内存
        except Exception as e:
            print(f"跟踪出错: {str(e)}")

        return frame

    def display_frame(self, frame):
        """显示帧到 QLabel"""
        # BGR 转 RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = rgb.shape
        bytes_per_line = c * w

        # 创建 QImage 并显示
        image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.screen.setPixmap(QPixmap.fromImage(image))
        self.screen.setScaledContents(True)

    def btn_detect_slot(self):
        """执行检测"""
        if not self.current_file:
            QMessageBox.warning(self, "警告", "请先加载文件")
            return

        if self.model is None:
            QMessageBox.critical(self, "错误", "模型未加载,无法进行检测")
            return

        if self.is_video:
            # 视频模式:切换实时检测状态
            self.is_detecting = not self.is_detecting

            if self.is_detecting:
                self.btn_detect.setText("停止检测")
                print("开始实时检测...")
                self.cleanup_video()
                self.play_video(self.video_path)
            else:
                self.btn_detect.setText("开始检测")
                print("停止检测")
                # # 重新播放原视频
                # self.cleanup_video()
                # self.play_video(self.video_path)
        else:
            # 图片模式:直接检测并显示
            self.detect_image()

    def detect_image(self):
        """检测图片"""
        try:
            # 显示进度对话框
            progress = QProgressDialog("正在检测图片...", None, 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.show()
            QApplication.processEvents()

            # 读取图片
            frame = cv2.imread(self.current_file)
            if frame is None:
                QMessageBox.warning(self, "警告", "无法读取图片文件")
                return

            # 进行检测
            results = self.model(frame)

            # 渲染结果
            frame = results[0].plot()  # 直接对单张结果调用plot()

            # 显示结果
            self.display_frame(frame)

            progress.close()

            # 显示检测结果统计
            # 获取单张图像的检测结果（DataFrame格式）
            # 获取检测框信息（boxes是 Boxes 对象）

            boxes = results[0].boxes  # 当前帧的检测框
            if len(boxes) > 0:
                class_counts = {}
                # 新增：存储每个目标的大小信息（可选）
                object_sizes = []  # 格式：[(类别名称, 宽度, 高度), ...]
                for box in boxes:
                    # 类别信息
                    cls_id = int(box.cls.item())
                    cls_name = self.model.names[cls_id]
                    # 计算目标大小（基于边界框坐标）
                    xyxy = box.xyxy[0].tolist()  # [xmin, ymin, xmax, ymax]
                    width = xyxy[2] - xyxy[0]  # 宽度 = xmax - xmin
                    height = xyxy[3] - xyxy[1]  # 高度 = ymax - ymin
                    object_sizes.append((cls_name, round(width, 2), round(height, 2)))  # 保留2位小数
                    # 统计类别数量
                    class_counts[cls_name] = class_counts.get(cls_name, 0) + 1
                # 构建提示信息（包含数量和大小）
                msg = "检测完成!\n\n检测到的目标:\n"
                for cls, count in class_counts.items():
                    msg += f"  {cls}: {count}个\n"
                # 可选：添加每个目标的大小详情
                msg += "\n目标大小（宽×高）:\n"
                for i, (cls, w, h) in enumerate(object_sizes, 1):
                    msg += f"  目标{i}（{cls}）: {w} × {h} 像素\n"
                QMessageBox.information(self, "检测结果", msg)
            else:
                QMessageBox.information(self, "检测结果", "未检测到任何目标")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"检测失败:\n{str(e)}")
    def btn_get_results_slot(self):
        if self.time_out == True:
            if not self.object_sizes:
                print("数据为空，无法保存")
                return
            else:
                print(3333)
                data = pd.DataFrame(
                    self.object_sizes,
                    # columns=["时间","编号","类别", "中心点x坐标(像素)", "中心点y坐标(像素)"]
                    columns=["时间","帧号","类别", "中心点x坐标(像素)", "中心点y坐标(像素)"]
                )
                # df_unique = data.drop_duplicates(subset=["编号"],keep="first")
                # # 保存为Excel（去除索引列）
                # df_unique.to_excel('result.xlsx', index=False)
                try:
                    data.to_excel('result.xlsx', index=False)
                except PermissionError:
                    print("文件被占用，请关闭后重试")
                except Exception as e:
                    print(f"保存文件失败：{e}")
                self.time_out = False

                # -------------帧跳转模块-----------------
                # 显示表格
                self._get_result_tabel()
                self.result_cap = cv2.VideoCapture("./processed_video.mp4")
                # 初始化帧跳转管理器（关键：传入主程序自身）

                self.frame_jump_manager = FrameJumpManager(self)

        else:
            QMessageBox.information(self, "提示", "请先检测")
            return


    def send2agent_slot(self):
        agent_text = main()
        self.agent_text.setText(agent_text)  # 正确设置显示内容
class SplashScreen(QMainWindow):
    """启动画面,用于显示模型加载进度"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("道路缺陷检测系统")
        self.setFixedSize(400, 200)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        label = QLabel("正在加载...", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setGeometry(0, 0, 400, 200)
        label.setStyleSheet("font-size: 20px; background-color: #2b2b2b; color: white;")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 显示启动画面
    splash = SplashScreen()
    splash.show()
    QApplication.processEvents()

    # 创建主窗口
    try:
        window = myWindow()
        splash.close()
        window.show()
    except Exception as e:
        splash.close()
        QMessageBox.critical(None, "启动失败", f"程序启动失败:\n{str(e)}")
        sys.exit(1)

    sys.exit(app.exec())