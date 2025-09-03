import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import socket
import struct
import time
import threading
import os
import pandas as pd
from tqdm import tqdm
import queue
import json

class MessageSenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("数据发送工具 - 可视化操作界面")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置窗口图标和样式
        self.root.configure(bg='#f0f0f0')
        
        # 变量初始化
        self.file_path = tk.StringVar()
        self.sheet_name = tk.StringVar(value="A")
        self.data_start_row = tk.StringVar(value="2")  # 数据起始行（从1开始计数）
        self.target_ip = tk.StringVar(value="127.0.0.1")
        self.target_port = tk.StringVar(value="5005")
        self.send_interval = tk.StringVar(value="0.1")
        
        # 控制变量
        self.is_running = False
        self.is_paused = False
        self.pause_flag = threading.Event()
        self.pause_flag.clear()
        self.stop_flag = threading.Event()
        self.stop_flag.clear()
        
        # 消息队列用于线程间通信
        self.message_queue = queue.Queue()
        
        # 数据包配置变量
        self.prefix_hex = tk.StringVar(value="55AA0000")
        self.suffix_hex = tk.StringVar(value="0000")
        self.int_columns_text = tk.StringVar(value="Speed_Ref_Int\nGross_Weight_Int\nGear_Status_Int")
        
        # 数据包配置（运行时计算）
        self.prefix = b'\x55\xAA\x00\x00'
        self.suffix = b'\x00\x00'
        self.int_columns = [
            'Speed_Ref_Int',
            'Gross_Weight_Int',
            'Gear_Status_Int'
        ]
        
        self.setup_ui()
        self.check_queue()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="数据发送工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件配置", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Excel文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.file_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.browse_file).grid(row=0, column=2)
        
        ttk.Label(file_frame, text="工作表:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.sheet_name, width=20).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(file_frame, text="数据起始行:").grid(row=1, column=2, sticky=tk.W, padx=(20, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.data_start_row, width=10).grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        
        # 网络配置区域
        network_frame = ttk.LabelFrame(main_frame, text="网络配置", padding="10")
        network_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        network_frame.columnconfigure(1, weight=1)
        
        ttk.Label(network_frame, text="目标IP:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(network_frame, textvariable=self.target_ip, width=20).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(network_frame, text="目标端口:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        ttk.Entry(network_frame, textvariable=self.target_port, width=10).grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(network_frame, text="发送间隔(秒):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(network_frame, textvariable=self.send_interval, width=10).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # 数据包配置区域
        packet_frame = ttk.LabelFrame(main_frame, text="数据包配置", padding="10")
        packet_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        packet_frame.columnconfigure(1, weight=1)
        
        ttk.Label(packet_frame, text="前缀(十六进制):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(packet_frame, textvariable=self.prefix_hex, width=20).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(packet_frame, text="后缀(十六进制):").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        ttk.Entry(packet_frame, textvariable=self.suffix_hex, width=10).grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(packet_frame, text="整数列名(每行一个):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        int_columns_text = scrolledtext.ScrolledText(packet_frame, height=4, width=60)
        int_columns_text.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        int_columns_text.insert(tk.END, self.int_columns_text.get())
        self.int_columns_widget = int_columns_text
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="开始发送", command=self.start_sending, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pause_button = ttk.Button(control_frame, text="暂停", command=self.pause_sending, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止", command=self.stop_sending, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 配置管理按钮
        ttk.Button(control_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="加载配置", command=self.load_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="生成解析脚本", command=self.generate_parser).pack(side=tk.LEFT)
        
        # 进度显示区域
        progress_frame = ttk.LabelFrame(main_frame, text="发送进度", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(progress_frame, text="就绪")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        self.stats_label = ttk.Label(progress_frame, text="")
        self.stats_label.grid(row=2, column=0, sticky=tk.W)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加一些示例数据
        self.log_message("程序已启动，请配置参数后点击'开始发送'")
        self.log_message("支持的操作：开始发送、暂停、继续、停止")
        
    def browse_file(self):
        """浏览选择Excel文件"""
        filename = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.log_message(f"已选择文件: {filename}")
    
    def parse_config(self):
        """解析用户配置"""
        try:
            # 解析前缀
            prefix_hex = self.prefix_hex.get().replace(" ", "").replace("0x", "").replace("0X", "")
            if len(prefix_hex) % 2 != 0:
                raise ValueError("前缀十六进制长度必须是偶数")
            self.prefix = bytes.fromhex(prefix_hex)
            
            # 解析后缀
            suffix_hex = self.suffix_hex.get().replace(" ", "").replace("0x", "").replace("0X", "")
            if len(suffix_hex) % 2 != 0:
                raise ValueError("后缀十六进制长度必须是偶数")
            self.suffix = bytes.fromhex(suffix_hex)
            
            # 解析整数列名
            int_columns_text = self.int_columns_widget.get("1.0", tk.END).strip()
            self.int_columns = [line.strip() for line in int_columns_text.split('\n') if line.strip()]
            
            return True
        except Exception as e:
            messagebox.showerror("配置错误", f"配置解析失败: {e}")
            return False
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_queue(self):
        """检查消息队列并更新UI"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                if message['type'] == 'log':
                    self.log_message(message['content'])
                elif message['type'] == 'progress':
                    self.progress_var.set(message['value'])
                elif message['type'] == 'status':
                    self.status_label.config(text=message['content'])
                elif message['type'] == 'stats':
                    self.stats_label.config(text=message['content'])
                elif message['type'] == 'complete':
                    self.on_sending_complete(message['data'])
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)
    
    def pack_row(self, row, columns):
        """打包行数据为二进制格式"""
        binary_data = self.prefix
        try:
            h, m, s, us = map(int, str(row[0]).split(':'))
            total_seconds = h * 3600 + m * 60 + s
            binary_data += struct.pack('>i', total_seconds)
            binary_data += struct.pack('>i', us)
        except Exception as e:
            self.message_queue.put({'type': 'log', 'content': f"[行: {row.name}] 解析时间戳 {row[0]} 时出错: {e}"})
            binary_data += struct.pack('>i', 0) * 2

        for i, value in enumerate(row[1:]):
            col = columns[i+1]
            try:
                if col in self.int_columns:
                    binary_data += struct.pack('>i', int(float(value)))
                else:
                    binary_data += struct.pack('>d', float(value))
            except Exception as e:
                self.message_queue.put({'type': 'log', 'content': f"[行: {row.name}] 处理值 {value} (列: {col}) 时出错: {e}"})
                binary_data += struct.pack('>i', 0) if col in self.int_columns else struct.pack('>d', 0.0)
        return binary_data + self.suffix
    
    def start_sending(self):
        """开始发送数据"""
        if not self.file_path.get():
            messagebox.showerror("错误", "请先选择Excel文件")
            return
        
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("错误", "选择的文件不存在")
            return
        
        try:
            target_port = int(self.target_port.get())
            send_interval = float(self.send_interval.get())
            data_start_row = int(self.data_start_row.get())
            if data_start_row < 1:
                raise ValueError("数据起始行必须大于0")
        except ValueError as e:
            messagebox.showerror("错误", f"参数错误: {e}")
            return
        
        # 解析配置
        if not self.parse_config():
            return
        
        self.is_running = True
        self.is_paused = False
        self.pause_flag.clear()
        self.stop_flag.clear()
        
        # 更新按钮状态
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        
        # 启动发送线程
        self.send_thread = threading.Thread(target=self.send_data_thread, daemon=True)
        self.send_thread.start()
        
        self.log_message("开始发送数据...")
        self.log_message(f"前缀: {self.prefix_hex.get()}")
        self.log_message(f"后缀: {self.suffix_hex.get()}")
        self.log_message(f"整数列: {len(self.int_columns)} 个")
    
    def save_config(self):
        """保存当前配置到文件"""
        config = {
            'file_path': self.file_path.get(),
            'sheet_name': self.sheet_name.get(),
            'data_start_row': self.data_start_row.get(),
            'target_ip': self.target_ip.get(),
            'target_port': self.target_port.get(),
            'send_interval': self.send_interval.get(),
            'prefix_hex': self.prefix_hex.get(),
            'suffix_hex': self.suffix_hex.get(),
            'int_columns': self.int_columns_widget.get("1.0", tk.END).strip()
        }
        
        filename = filedialog.asksaveasfilename(
            title="保存配置",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                self.log_message(f"配置已保存到: {filename}")
                messagebox.showinfo("成功", "配置保存成功！")
            except Exception as e:
                messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def load_config(self):
        """从文件加载配置"""
        filename = filedialog.askopenfilename(
            title="加载配置",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 加载配置到界面
                self.file_path.set(config.get('file_path', ''))
                self.sheet_name.set(config.get('sheet_name', 'A'))
                self.data_start_row.set(config.get('data_start_row', '2'))
                self.target_ip.set(config.get('target_ip', '127.0.0.1'))
                self.target_port.set(config.get('target_port', '5005'))
                self.send_interval.set(config.get('send_interval', '0.1'))
                self.prefix_hex.set(config.get('prefix_hex', '55AA0000'))
                self.suffix_hex.set(config.get('suffix_hex', '0000'))
                
                # 更新整数列文本框
                self.int_columns_widget.delete("1.0", tk.END)
                self.int_columns_widget.insert("1.0", config.get('int_columns', ''))
                
                self.log_message(f"配置已从文件加载: {filename}")
                messagebox.showinfo("成功", "配置加载成功！")
            except Exception as e:
                messagebox.showerror("错误", f"加载配置失败: {e}")
    
    def generate_parser(self):
        """生成数据包解析脚本"""
        if not self.file_path.get():
            messagebox.showerror("错误", "请先选择Excel文件以获取列信息")
            return
        
        try:
            # 读取Excel文件获取列信息
            df = pd.read_excel(self.file_path.get(), sheet_name=self.sheet_name.get())
            columns = df.columns.tolist()
            
            # 解析当前配置
            if not self.parse_config():
                return
            
            # 生成MATLAB解析脚本
            matlab_script = self.generate_matlab_parser(columns)
            
            # 保存脚本
            filename = filedialog.asksaveasfilename(
                title="保存解析脚本",
                defaultextension=".m",
                filetypes=[("MATLAB脚本", "*.m"), ("所有文件", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(matlab_script)
                
                self.log_message(f"解析脚本已生成: {filename}")
                messagebox.showinfo("成功", f"MATLAB解析脚本已生成！\n文件位置: {filename}")
                
        except Exception as e:
            messagebox.showerror("错误", f"生成解析脚本失败: {e}")
    
    def generate_matlab_parser(self, columns):
        """生成MATLAB数据包解析脚本"""
        prefix_hex = self.prefix_hex.get()
        suffix_hex = self.suffix_hex.get()
        int_columns = self.int_columns
        
        # 计算数据包结构
        prefix_bytes = len(prefix_hex) // 2
        suffix_bytes = len(suffix_hex) // 2
        timestamp_bytes = 8  # 4字节秒数 + 4字节微秒
        data_columns = len(columns) - 1  # 减去时间戳列
        
        # 计算每列的数据类型和字节数
        column_info = []
        for i, col in enumerate(columns[1:], 1):  # 跳过第一列（时间戳）
            if col in int_columns:
                column_info.append(f"    % 列{i}: {col} (int32, 4字节)")
            else:
                column_info.append(f"    % 列{i}: {col} (double, 8字节)")
        
        # 生成MATLAB脚本
        script = f"""function [timestamp, data] = parse_udp_packet(packet_data)
% UDP数据包解析函数
% 自动生成于: {time.strftime('%Y-%m-%d %H:%M:%S')}
% 
% 输入: packet_data - 接收到的UDP数据包（字节数组）
% 输出: timestamp - 时间戳 [小时, 分钟, 秒, 微秒]
%       data - 解析后的数据 [列1, 列2, ...]

% 数据包结构配置
PREFIX_HEX = '{prefix_hex}';  % 前缀
SUFFIX_HEX = '{suffix_hex}';  % 后缀
PREFIX_BYTES = {prefix_bytes};  % 前缀字节数
SUFFIX_BYTES = {suffix_bytes};  % 后缀字节数
TIMESTAMP_BYTES = {timestamp_bytes};  % 时间戳字节数

% 列信息:
{chr(10).join(column_info)}

% 计算总数据包大小
total_data_bytes = {sum(4 if col in int_columns else 8 for col in columns[1:])};
expected_packet_size = PREFIX_BYTES + TIMESTAMP_BYTES + total_data_bytes + SUFFIX_BYTES;

% 检查数据包大小
if length(packet_data) ~= expected_packet_size
    error('数据包大小不匹配: 期望 %d 字节, 实际 %d 字节', expected_packet_size, length(packet_data));
end

% 解析前缀
prefix = packet_data(1:PREFIX_BYTES);
expected_prefix = hex2dec(reshape(PREFIX_HEX, 2, [])')';
if ~isequal(prefix, expected_prefix)
    warning('前缀不匹配');
end

% 解析时间戳
timestamp_start = PREFIX_BYTES + 1;
timestamp_end = PREFIX_BYTES + TIMESTAMP_BYTES;
timestamp_bytes = packet_data(timestamp_start:timestamp_end);

% 转换时间戳（大端序）
seconds = typecast(timestamp_bytes(1:4), 'uint32');
microseconds = typecast(timestamp_bytes(5:8), 'uint32');

% 转换为时分秒格式
hours = floor(seconds / 3600);
minutes = floor(mod(seconds, 3600) / 60);
secs = mod(seconds, 60);
timestamp = [hours, minutes, secs, microseconds];

% 解析数据列
data_start = PREFIX_BYTES + TIMESTAMP_BYTES + 1;
data = zeros(1, {len(columns)-1});
byte_offset = 0;

"""
        
        # 添加每列的解析代码
        for i, col in enumerate(columns[1:], 1):
            if col in int_columns:
                script += f"""
% 解析列{i}: {col} (int32)
col_start = data_start + byte_offset;
col_end = col_start + 3;
data({i}) = typecast(packet_data(col_start:col_end), 'int32');
byte_offset = byte_offset + 4;
"""
            else:
                script += f"""
% 解析列{i}: {col} (double)
col_start = data_start + byte_offset;
col_end = col_start + 7;
data({i}) = typecast(packet_data(col_start:col_end), 'double');
byte_offset = byte_offset + 8;
"""
        
        script += f"""
% 检查后缀
suffix_start = data_start + byte_offset;
suffix_end = suffix_start + SUFFIX_BYTES - 1;
suffix = packet_data(suffix_start:suffix_end);
expected_suffix = hex2dec(reshape(SUFFIX_HEX, 2, [])')';
if ~isequal(suffix, expected_suffix)
    warning('后缀不匹配');
end

% 显示解析结果
fprintf('时间戳: %02d:%02d:%02d.%06d\\n', hours, minutes, secs, microseconds);
fprintf('数据: ');
for i = 1:length(data)
    fprintf('%s=%.6f ', '{columns[i+1] if i+1 < len(columns) else "col" + str(i)}', data(i));
end
fprintf('\\n');

end

% 使用示例:
% [timestamp, data] = parse_udp_packet(received_packet);
% 
% 批量解析示例:
% for i = 1:length(packet_buffer)
%     [ts, dt] = parse_udp_packet(packet_buffer{{i}});
%     % 处理解析后的数据
% end
"""
        
        return script
    
    def pause_sending(self):
        """暂停/继续发送"""
        if self.is_paused:
            self.pause_flag.clear()
            self.is_paused = False
            self.pause_button.config(text="暂停")
            self.log_message("已继续发送")
        else:
            self.pause_flag.set()
            self.is_paused = True
            self.pause_button.config(text="继续")
            self.log_message("已暂停发送")
    
    def stop_sending(self):
        """停止发送"""
        self.stop_flag.set()
        self.pause_flag.set()  # 确保暂停
        self.log_message("正在停止发送...")
    
    def on_sending_complete(self, data):
        """发送完成后的处理"""
        self.is_running = False
        self.is_paused = False
        
        # 更新按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="暂停")
        self.stop_button.config(state=tk.DISABLED)
        
        # 显示统计信息
        self.log_message("===== 操作完成 =====")
        self.log_message(f"成功发送: {data['total_sent']} 条记录")
        self.log_message(f"跳过处理: {data['skipped']} 条记录")
        self.log_message(f"总共处理: {data['total_records']} 条记录")
        self.log_message(f"总耗时: {data['elapsed']:.2f} 秒")
        if data['total_sent'] > 0:
            self.log_message(f"平均发送间隔: {data['elapsed']/data['total_sent']:.4f} 秒/条")
    
    def send_data_thread(self):
        """发送数据的工作线程"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 读取Excel文件
            self.message_queue.put({'type': 'status', 'content': '正在读取文件...'})
            df = pd.read_excel(self.file_path.get(), sheet_name=self.sheet_name.get())
            self.message_queue.put({'type': 'log', 'content': f"成功读取文件，共 {len(df)} 行数据"})
            
            columns = df.columns.tolist()
            data_start_row = int(self.data_start_row.get())
            data_rows = df.iloc[data_start_row-1:]  # 转换为0基索引
            total_records = len(data_rows)
            self.message_queue.put({'type': 'log', 'content': f"开始发送数据，总共 {total_records} 条记录..."})
            
            sent_idx_set = set()
            last_binary_data = None
            last_idx = None
            total_sent = skipped = 0
            start_time = time.time()
            
            data_iter = data_rows.iterrows()
            
            while len(sent_idx_set) < total_records and not self.stop_flag.is_set():
                if not self.pause_flag.is_set():
                    try:
                        idx, row = next(data_iter)
                    except StopIteration:
                        break
                    binary_data = self.pack_row(row, columns)
                    last_binary_data = binary_data
                    last_idx = idx
                    sent_idx_set.add(idx)
                else:
                    if last_binary_data is not None and last_idx is not None:
                        binary_data = last_binary_data
                        idx = last_idx
                    else:
                        time.sleep(float(self.send_interval.get()))
                        continue

                try:
                    sock.sendto(binary_data, (self.target_ip.get(), int(self.target_port.get())))
                    if not self.pause_flag.is_set():
                        total_sent += 1
                        progress = (len(sent_idx_set) / total_records) * 100
                        self.message_queue.put({'type': 'progress', 'value': progress})
                        self.message_queue.put({'type': 'stats', 'content': f"已发送: {total_sent}/{total_records}"})
                except Exception as e:
                    skipped += 1
                    self.message_queue.put({'type': 'log', 'content': f"发送错误: {e}"})
                
                time.sleep(float(self.send_interval.get()))

            elapsed = time.time() - start_time
            
            # 发送完成消息
            self.message_queue.put({
                'type': 'complete',
                'data': {
                    'total_sent': total_sent,
                    'skipped': skipped,
                    'total_records': total_records,
                    'elapsed': elapsed
                }
            })
            
        except Exception as e:
            self.message_queue.put({'type': 'log', 'content': f"发生错误: {e}"})
            self.message_queue.put({'type': 'complete', 'data': {'total_sent': 0, 'skipped': 0, 'total_records': 0, 'elapsed': 0}})
        finally:
            sock.close()
            self.message_queue.put({'type': 'log', 'content': "Socket连接已关闭"})

def main():
    root = tk.Tk()
    app = MessageSenderGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("退出", "程序正在运行，确定要退出吗？"):
                app.stop_sending()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
