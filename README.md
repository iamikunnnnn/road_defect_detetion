# 道路缺陷检测系统

## 概述
道路缺陷检测系统是一款基于计算机视觉技术的应用程序，能够使用YOLOv11模型对视频或图像中的道路缺陷进行自动检测，并结合Gemini AI模型对检测结果进行专业分析。该系统提供了直观的用户界面，支持视频/图像加载、实时检测、结果查看和AI分析等功能。

## 功能特点
- 支持加载视频文件（.mp4、.avi）和图像文件（.jpg、.jpeg、.png）
- 利用YOLOv11模型进行实时缺陷检测与跟踪
- 检测结果可视化展示，包含目标框和类别信息
- 生成详细的检测结果表格，记录缺陷出现的时间、帧号、类别和位置
- 支持通过表格点击快速跳转到对应帧查看缺陷
- 基于Gemini AI模型对检测结果进行专业分析，包括时间维度、帧序列模式、空间分布特征和类别间关系

## 安装要求
- Python 3.x
- 相关依赖库：PyQt6、OpenCV、PyTorch、Pandas、Ultralytics、Google Generative AI

## 环境配置
1. 安装Python 3.x环境
2. 安装依赖库：
```bash
pip install PyQt6 opencv-python torch pandas ultralytics google-generativeai
```
3. 配置网络代理（系统已预设本地代理地址http://127.0.0.1:7000，如需修改请在代码中调整）

## 使用方法
1. 运行主程序：
```bash
python app.py
```
2. 程序启动后，点击"加载文件"按钮选择视频或图像文件
3. 点击"开始检测"按钮进行缺陷检测：
   - 视频文件：实时播放并检测，可点击"停止检测"终止
   - 图像文件：直接进行检测并显示结果
4. 检测完成后，点击"获取结果"生成结果表格
5. 在结果表格中点击任意行可跳转到对应帧查看缺陷
6. 点击"发送到AI分析"按钮获取Gemini AI的专业分析结果

## 项目结构
- `app.py`：主程序文件，包含UI交互和检测逻辑
- `analyze_gemini.py`：处理检测结果并与Gemini AI交互的模块
- `view_frame_manager.py`：实现帧跳转功能的模块
- `UI.ui`：PyQt6界面设计文件
- `yolov11m.engine`：YOLOv11模型权重文件（需自行准备）

## 注意事项
- 确保`UI.ui`文件和YOLOv11模型权重文件`yolov11m.engine`在程序运行目录下
- 首次运行时模型加载可能需要较长时间
- 视频检测完成后会生成`processed_video.mp4`文件保存检测结果
- 检测结果会保存为`result.xlsx`文件，用于AI分析
- 使用AI分析功能需要有效的网络连接和Gemini API密钥

