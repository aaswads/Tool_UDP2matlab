# UDP Data Sender

一个通用的UDP数据发送工具，可以将Excel文件中的数据通过UDP协议发送到指定的网络地址。支持完全图形化配置，自动生成MATLAB解析脚本。

## ✨ 特性

- 🖥️ **完全图形化界面** - 无需编程知识，所有配置通过界面完成
- 📊 **Excel数据支持** - 支持.xlsx和.xls格式的Excel文件
- 🔧 **灵活配置** - 可自定义数据包格式、网络参数、数据类型等
- 📝 **自动解析脚本** - 自动生成MATLAB数据包解析脚本
- 💾 **配置管理** - 支持保存和加载配置文件
- ⏸️ **实时控制** - 支持暂停、继续、停止操作
- 📈 **进度监控** - 实时显示发送进度和统计信息

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python udp_data_sender.py
```

### 打包为可执行文件

```bash
python build.py
```

## 📖 使用说明

### 1. 文件配置

- **Excel文件**: 选择要发送的Excel文件
- **工作表**: 指定工作表名称（默认为"A"）
- **数据起始行**: 设置数据开始的行号（默认为2，跳过标题行）

### 2. 网络配置

- **目标IP**: 接收数据的IP地址
- **目标端口**: 接收数据的端口号
- **发送间隔**: 数据包发送间隔（秒）

### 3. 数据包配置

- **前缀**: 数据包前缀（十六进制，如"55AA0000"）
- **后缀**: 数据包后缀（十六进制，如"0000"）
- **整数列名**: 需要作为整数处理的列名列表

### 4. 生成解析脚本

点击"生成解析脚本"按钮，程序会自动：
- 分析Excel文件结构
- 根据当前配置生成MATLAB解析函数
- 保存为.m文件，可直接在MATLAB中使用

## 📊 数据格式

### 发送格式

数据包结构：`前缀 + 时间戳 + 数据 + 后缀`

- **时间戳**: 8字节（4字节秒数 + 4字节微秒）
- **数据列**: 根据配置决定数据类型
  - 整数列：4字节int32
  - 浮点列：8字节double

### Excel文件要求

- 第一列：时间戳（格式：HH:MM:SS:微秒）
- 后续列：数据列，列名用于配置数据类型

## 🔧 配置示例

### 配置文件格式 (config_example.json)

```json
{
  "file_path": "data.xlsx",
  "sheet_name": "A",
  "data_start_row": "2",
  "target_ip": "127.0.0.1",
  "target_port": "5005",
  "send_interval": "0.1",
  "prefix_hex": "55AA0000",
  "suffix_hex": "0000",
  "int_columns": "Column1\nColumn2\nColumn3"
}
```

### MATLAB解析脚本示例

生成的MATLAB脚本包含完整的解析函数：

```matlab
function [timestamp, data] = parse_udp_packet(packet_data)
% 自动生成的UDP数据包解析函数
% 输入: packet_data - 接收到的UDP数据包
% 输出: timestamp - 时间戳 [小时, 分钟, 秒, 微秒]
%       data - 解析后的数据数组

% 使用示例:
[timestamp, data] = parse_udp_packet(received_packet);
```

## 📁 项目结构

```
UDP-Data-Sender/
├── udp_data_sender.py      # 主程序
├── build.py                # 打包脚本
├── requirements.txt        # 依赖列表
├── config_example.json     # 配置示例
├── README.md              # 项目说明
└── 10106-20231219-ROAAS-Landing.xlsx  # 示例数据文件
```

## 🛠️ 开发

### 依赖项

- Python 3.7+
- tkinter (内置)
- pandas
- openpyxl
- tqdm

### 构建

```bash
# 安装PyInstaller
pip install pyinstaller

# 构建可执行文件
python build.py
```

## 📝 使用场景

- **数据采集系统**: 将传感器数据通过UDP发送到处理系统
- **仿真测试**: 发送测试数据到仿真环境
- **数据同步**: 在不同系统间同步数据
- **实时监控**: 实时发送监控数据

## ⚠️ 注意事项

1. 确保目标IP和端口正确，且接收端程序正在运行
2. Excel文件格式必须符合要求（第一列为时间戳）
3. 十六进制配置必须是偶数长度
4. 整数列名必须与Excel中的列名完全匹配
5. 发送间隔不宜设置过小，避免网络拥塞

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [PyInstaller文档](https://pyinstaller.readthedocs.io/)
- [pandas文档](https://pandas.pydata.org/docs/)
- [tkinter文档](https://docs.python.org/3/library/tkinter.html)

---

**版本**: 2.0  
**更新日期**: 2024年  
**支持系统**: Windows 10/11, Linux, macOS
