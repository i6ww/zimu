"""
SRT 字幕文件生成工具
"""
from typing import List, Dict


def generate_srt(subtitles: List[Dict]) -> str:
    """
    生成 SRT 格式字幕
    
    Args:
        subtitles: 字幕列表
        [{
            "index": 1,
            "begin_time": 0.0,
            "end_time": 2.5,
            "text": "字幕文本"
        }, ...]
        
    Returns:
        SRT 格式字符串
    """
    srt_lines = []
    
    for sub in subtitles:
        index = sub.get('index', 1)
        start = seconds_to_srt_time(sub['begin_time'])
        end = seconds_to_srt_time(sub['end_time'])
        text = sub['text']
        
        srt_lines.append(f"{index}")
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(f"{text}")
        srt_lines.append("")  # 空行分隔
    
    return '\n'.join(srt_lines)


def seconds_to_srt_time(seconds: float) -> str:
    """
    将秒数转换为 SRT 时间格式
    
    Args:
        seconds: 秒数（支持浮点数）
        
    Returns:
        SRT 时间字符串 "00:00:00,000"
    """
    if seconds < 0:
        seconds = 0
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def parse_srt(srt_content: str) -> List[Dict]:
    """
    解析 SRT 文件内容
    
    Args:
        srt_content: SRT 文件字符串
        
    Returns:
        字幕列表
    """
    subtitles = []
    blocks = srt_content.strip().split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                index = int(lines[0])
                time_line = lines[1]
                text = '\n'.join(lines[2:])
                
                # 解析时间
                start_str, end_str = time_line.split(' --> ')
                start = srt_time_to_seconds(start_str)
                end = srt_time_to_seconds(end_str)
                
                subtitles.append({
                    'index': index,
                    'begin_time': start,
                    'end_time': end,
                    'text': text
                })
            except (ValueError, IndexError):
                continue  # 跳过格式错误的块
    
    return subtitles


def srt_time_to_seconds(time_str: str) -> float:
    """
    将 SRT 时间字符串转换为秒数
    
    Args:
        time_str: SRT 时间字符串 "00:00:00,000"
        
    Returns:
        秒数
    """
    # 替换逗号为冒号以便解析
    time_str = time_str.replace(',', ':')
    parts = time_str.split(':')
    
    if len(parts) == 4:
        h = int(parts[0])
        m = int(parts[1])
        s = int(parts[2])
        ms = int(parts[3])
        return h * 3600 + m * 60 + s + ms / 1000.0
    
    return 0.0


def validate_subtitles(subtitles: List[Dict]) -> tuple:
    """
    验证字幕列表的有效性
    
    Args:
        subtitles: 字幕列表
        
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    for i, sub in enumerate(subtitles):
        index = i + 1
        
        # 检查必需字段
        if 'text' not in sub or not sub['text']:
            errors.append(f"字幕 {index}: 缺少文本内容")
            continue
        
        # 检查时间
        begin = sub.get('begin_time', 0)
        end = sub.get('end_time', 0)
        
        if begin < 0:
            errors.append(f"字幕 {index}: 开始时间不能为负数")
        
        if end < 0:
            errors.append(f"字幕 {index}: 结束时间不能为负数")
        
        if end > 0 and begin >= end:
            errors.append(f"字幕 {index}: 开始时间必须小于结束时间")
    
    return len(errors) == 0, errors
