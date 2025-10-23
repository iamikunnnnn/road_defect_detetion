import subprocess
import sys
import os

# 获取 app.py 的绝对路径（与 a.exe 同目录）
app_path = os.path.join(
    os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__),
    "app.py"
)

# 指定虚拟环境中的 python.exe
python_path = r"D:\anaconda\envs\road_defect_detection_yolov11\python.exe"

# 调用 Python 运行 app.py
subprocess.run([python_path, app_path])