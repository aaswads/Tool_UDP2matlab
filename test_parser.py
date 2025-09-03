#!/usr/bin/env python3
"""
测试脚本 - 验证数据包解析功能

这个脚本用于测试生成的MATLAB解析脚本的正确性。
"""

import struct
import time

def create_test_packet():
    """创建测试数据包"""
    # 配置
    prefix = b'\x55\xAA\x00\x00'
    suffix = b'\x00\x00'
    
    # 时间戳 (1小时2分3秒456789微秒)
    hours, minutes, seconds = 1, 2, 3
    microseconds = 456789
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    timestamp_data = struct.pack('>i', total_seconds) + struct.pack('>i', microseconds)
    
    # 测试数据
    int_data = struct.pack('>i', 12345)  # 整数
    float_data = struct.pack('>d', 3.14159)  # 浮点数
    
    # 组装数据包
    packet = prefix + timestamp_data + int_data + float_data + suffix
    
    return packet

def test_packet_structure():
    """测试数据包结构"""
    packet = create_test_packet()
    
    print("测试数据包结构:")
    print(f"总长度: {len(packet)} 字节")
    print(f"前缀: {packet[:4].hex().upper()}")
    print(f"时间戳: {packet[4:12].hex().upper()}")
    print(f"整数数据: {packet[12:16].hex().upper()}")
    print(f"浮点数据: {packet[16:24].hex().upper()}")
    print(f"后缀: {packet[24:26].hex().upper()}")
    
    # 解析验证
    prefix = packet[:4]
    timestamp_bytes = packet[4:12]
    int_bytes = packet[12:16]
    float_bytes = packet[16:24]
    suffix = packet[24:26]
    
    # 解析时间戳
    seconds = struct.unpack('>i', timestamp_bytes[:4])[0]
    microseconds = struct.unpack('>i', timestamp_bytes[4:8])[0]
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    print(f"\n解析结果:")
    print(f"时间戳: {hours:02d}:{minutes:02d}:{secs:02d}.{microseconds:06d}")
    print(f"整数: {struct.unpack('>i', int_bytes)[0]}")
    print(f"浮点数: {struct.unpack('>d', float_bytes)[0]}")
    
    return packet

if __name__ == "__main__":
    print("UDP Data Sender - 数据包解析测试")
    print("=" * 50)
    
    test_packet = test_packet_structure()
    
    print(f"\n测试数据包 (十六进制):")
    print(test_packet.hex().upper())
    
    print("\n测试完成！")
    print("可以将此数据包用于测试MATLAB解析脚本。")
