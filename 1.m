function [timestamp, data] = parse_udp_packet(packet_data)
% UDP数据包解析函数
% 自动生成于: 2025-09-02 14:21:05
% 
% 输入: packet_data - 接收到的UDP数据包（字节数组）
% 输出: timestamp - 时间戳 [小时, 分钟, 秒, 微秒]
%       data - 解析后的数据 [列1, 列2, ...]

% 数据包结构配置
PREFIX_HEX = '55AA0000';  % 前缀
SUFFIX_HEX = '0000';  % 后缀
PREFIX_BYTES = 4;  % 前缀字节数
SUFFIX_BYTES = 2;  % 后缀字节数
TIMESTAMP_BYTES = 8;  % 时间戳字节数

% 列信息:
    % 列1: Speed_Ref_Int (int32, 4字节)
    % 列2: Gross_Weight_Int (int32, 4字节)
    % 列3: Gear_Status_Int (int32, 4字节)
    % 列4: Altitude_Double (double, 8字节)
    % 列5: Airspeed_Double (double, 8字节)

% 计算总数据包大小
total_data_bytes = 28;
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
data = zeros(1, 5);
byte_offset = 0;


% 解析列1: Speed_Ref_Int (int32)
col_start = data_start + byte_offset;
col_end = col_start + 3;
data(1) = typecast(packet_data(col_start:col_end), 'int32');
byte_offset = byte_offset + 4;

% 解析列2: Gross_Weight_Int (int32)
col_start = data_start + byte_offset;
col_end = col_start + 3;
data(2) = typecast(packet_data(col_start:col_end), 'int32');
byte_offset = byte_offset + 4;

% 解析列3: Gear_Status_Int (int32)
col_start = data_start + byte_offset;
col_end = col_start + 3;
data(3) = typecast(packet_data(col_start:col_end), 'int32');
byte_offset = byte_offset + 4;

% 解析列4: Altitude_Double (double)
col_start = data_start + byte_offset;
col_end = col_start + 7;
data(4) = typecast(packet_data(col_start:col_end), 'double');
byte_offset = byte_offset + 8;

% 解析列5: Airspeed_Double (double)
col_start = data_start + byte_offset;
col_end = col_start + 7;
data(5) = typecast(packet_data(col_start:col_end), 'double');
byte_offset = byte_offset + 8;

% 检查后缀
suffix_start = data_start + byte_offset;
suffix_end = suffix_start + SUFFIX_BYTES - 1;
suffix = packet_data(suffix_start:suffix_end);
expected_suffix = hex2dec(reshape(SUFFIX_HEX, 2, [])')';
if ~isequal(suffix, expected_suffix)
    warning('后缀不匹配');
end

% 显示解析结果
fprintf('时间戳: %02d:%02d:%02d.%06d\n', hours, minutes, secs, microseconds);
fprintf('数据: ');
for i = 1:length(data)
    fprintf('%s=%.6f ', 'col5', data(i));
end
fprintf('\n');

end

% 使用示例:
% [timestamp, data] = parse_udp_packet(received_packet);
% 
% 批量解析示例:
% for i = 1:length(packet_buffer)
%     [ts, dt] = parse_udp_packet(packet_buffer{i});
%     % 处理解析后的数据
% end
