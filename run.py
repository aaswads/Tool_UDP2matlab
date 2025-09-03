#!/usr/bin/env python3
"""
UDP Data Sender - 启动脚本

简单的启动脚本，用于运行UDP数据发送工具。
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from udp_data_sender import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖项: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"运行错误: {e}")
    sys.exit(1)
