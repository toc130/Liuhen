"""
时间工具模块 - 处理时间相关的功能
"""

import datetime
import time
from src.config import TIME_FORMAT, INTERVAL_REMINDER_MINUTES


def get_current_time_str():
    """
    获取当前时间的格式化字符串
    
    Returns:
        str: 格式化的时间字符串
    """
    return datetime.datetime.now().strftime(TIME_FORMAT)


def format_timestamp(timestamp, format_str=TIME_FORMAT):
    """
    将时间戳格式化为字符串
    
    Args:
        timestamp: datetime对象或时间戳
        format_str: 格式化字符串
        
    Returns:
        str: 格式化的时间字符串
    """
    if isinstance(timestamp, datetime.datetime):
        return timestamp.strftime(format_str)
    return datetime.datetime.fromtimestamp(timestamp).strftime(format_str)


def parse_time_string(time_str):
    """
    解析时间字符串为时分
    
    Args:
        time_str: 时间字符串，格式为 "HH:MM"
        
    Returns:
        tuple: (小时, 分钟) 或 None（如果解析失败）
    """
    try:
        if ":" in time_str:
            hours, minutes = time_str.split(":")
            hours = int(hours)
            minutes = int(minutes)
            
            # 验证时间的有效性
            if 0 <= hours < 24 and 0 <= minutes < 60:
                return hours, minutes
    except:
        pass
    
    return None


def calculate_next_reminder_time(hours, minutes):
    """
    计算下一次提醒的时间
    
    Args:
        hours: 小时 (0-23)
        minutes: 分钟 (0-59)
        
    Returns:
        datetime: 下一次提醒的时间
    """
    now = datetime.datetime.now()
    target_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
    
    # 如果目标时间已经过去，则设置为明天的这个时间
    if target_time <= now:
        target_time += datetime.timedelta(days=1)
    
    return target_time


def calculate_next_interval_reminder():
    """
    计算下一次间隔提醒的时间（从当前时间起指定分钟后）
    
    Returns:
        datetime: 下一次间隔提醒的时间
    """
    now = datetime.datetime.now()
    # 添加指定的分钟数
    target_time = now + datetime.timedelta(minutes=INTERVAL_REMINDER_MINUTES)
    return target_time


def time_until_next_reminder(next_reminder_time):
    """
    计算距离下一次提醒还有多少时间（秒）
    
    Args:
        next_reminder_time: datetime对象，下一次提醒的时间
        
    Returns:
        int: 距离下一次提醒的秒数
    """
    now = datetime.datetime.now()
    time_delta = next_reminder_time - now
    return time_delta.total_seconds()


def format_time_delta(seconds):
    """
    格式化时间差为人类可读格式
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的时间差字符串（如 "2小时30分钟"）
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}小时{minutes}分钟"
    elif minutes > 0:
        return f"{minutes}分钟{seconds}秒"
    else:
        return f"{seconds}秒"