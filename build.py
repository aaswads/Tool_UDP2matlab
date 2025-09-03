"""
打包脚本 - 将GUI程序打包成可执行文件
使用PyInstaller将Python程序打包成exe文件，无需安装Python环境即可运行
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功！")
        return True
    except subprocess.CalledProcessError:
        print("PyInstaller安装失败！")
        return False

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--windowed",                   # 不显示控制台窗口
        "--name=数据发送工具",           # 可执行文件名称
        "--icon=icon.ico",              # 图标文件（如果存在）
        "--add-data=*.xlsx;.",          # 包含Excel文件
        "--hidden-import=pandas",       # 确保pandas被包含
        "--hidden-import=openpyxl",     # 确保openpyxl被包含
        "--hidden-import=tqdm",         # 确保tqdm被包含
        "udp_data_sender.py"            # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    try:
        subprocess.check_call(cmd)
        print("可执行文件构建成功！")
        print("生成的文件位置: dist/数据发送工具.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

def create_requirements():
    """创建requirements.txt文件"""
    requirements = [
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        "tqdm>=4.60.0"
    ]
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(requirements))
    
    print("已创建requirements.txt文件")

def create_readme():
    """创建使用说明文档"""
    readme_content = """# 数据发送工具 - 使用说明

## 功能简介
这是一个可视化的数据发送工具，可以将Excel文件中的数据通过UDP协议发送到指定的网络地址。所有配置都可以通过图形界面进行设置，无需修改代码。

## 使用方法

### 1. 文件配置
- **Excel文件**: 点击"浏览"按钮选择要发送的Excel文件
- **工作表**: 输入Excel文件中的工作表名称（默认为"A"）
- **数据起始行**: 设置数据开始的行号，从1开始计数（默认为2，即跳过标题行）

### 2. 网络配置
- **目标IP**: 输入接收数据的IP地址（默认为127.0.0.1）
- **目标端口**: 输入接收数据的端口号（默认为5005）
- **发送间隔**: 设置每条数据之间的发送间隔，单位为秒（默认为0.1秒）

### 3. 数据包配置
- **前缀(十六进制)**: 设置数据包的前缀，如"55AA0000"
- **后缀(十六进制)**: 设置数据包的后缀，如"0000"
- **整数列名**: 列出需要作为整数处理的列名，每行一个

### 4. 配置管理
- **保存配置**: 将当前所有配置保存到JSON文件，方便下次使用
- **加载配置**: 从JSON文件加载之前保存的配置

### 5. 开始发送
- 点击"开始发送"按钮开始发送数据
- 程序会显示发送进度和统计信息
- 可以通过"暂停"、"继续"、"停止"按钮控制发送过程

### 6. 查看日志
- 在"操作日志"区域可以查看详细的运行信息
- 包括错误信息、发送状态、配置信息等

## 数据格式说明
程序会将Excel数据打包成二进制格式发送：
1. 第一列作为时间戳（格式：HH:MM:SS:微秒）
2. 后续列根据配置决定是整数还是浮点数
3. 数据包格式：前缀 + 时间戳 + 数据 + 后缀

## 注意事项
1. 确保目标IP和端口正确，且接收端程序正在运行
2. Excel文件格式必须符合程序要求（第一列为时间戳）
3. 发送间隔不宜设置过小，避免网络拥塞
4. 程序支持暂停和继续功能，可以随时控制发送过程
5. 十六进制配置必须是偶数长度，如"55AA"、"0000"等
6. 整数列名必须与Excel中的列名完全匹配

## 配置示例
- 前缀: 55AA0000
- 后缀: 0000
- 整数列示例:
  ```
  Speed_Ref_Int
  Gross_Weight_Int
  Gear_Status_Int
  ```

## 技术支持
如有问题，请检查：
1. Excel文件格式是否正确
2. 网络连接是否正常
3. 目标IP和端口是否正确
4. 防火墙设置是否允许UDP通信
5. 数据包配置是否正确
6. 整数列名是否与Excel列名匹配

## 版本信息
- 版本: 2.0
- 更新日期: 2024年
- 支持系统: Windows 10/11
- 新增功能: 完全图形化配置、配置保存/加载
"""
    
    with open("使用说明.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("已创建使用说明.txt文件")

def main():
    """主函数"""
    print("=" * 50)
    print("数据发送工具 - 打包脚本")
    print("=" * 50)
    
    # 检查必要文件
    if not os.path.exists("udp_data_sender.py"):
        print("错误: 找不到udp_data_sender.py文件！")
        return
    
    # 创建说明文档
    create_requirements()
    create_readme()
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return
    
    # 构建可执行文件
    if build_executable():
        print("\n" + "=" * 50)
        print("打包完成！")
        print("=" * 50)
        print("生成的文件:")
        print("- dist/数据发送工具.exe (主程序)")
        print("- 使用说明.txt (使用说明)")
        print("- requirements.txt (依赖列表)")
        print("\n使用说明:")
        print("1. 将dist/数据发送工具.exe复制到目标电脑")
        print("2. 双击运行即可，无需安装Python环境")
        print("3. 参考使用说明.txt了解详细使用方法")
    else:
        print("打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
