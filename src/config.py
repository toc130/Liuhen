"""
配置文件 - 存储应用程序的全局配置
"""

import os

# 应用程序基本配置
APP_NAME = "留痕软件"
APP_VERSION = "1.0.0"
APP_WINDOW_SIZE = "1024x768"  # 更大的默认窗口尺寸

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCREENSHOT_DIR = os.path.join(DATA_DIR, "screenshots")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 确保目录存在
def ensure_dirs():
    """确保所有必要的目录都存在"""
    for directory in [DATA_DIR, SCREENSHOT_DIR, LOG_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

# 浅色主题颜色配置
COLOR_PRIMARY = "#3498db"     # 主要颜色
COLOR_SUCCESS = "#2ecc71"     # 成功/确认颜色
COLOR_WARNING = "#f39c12"     # 警告颜色
COLOR_DANGER = "#e74c3c"      # 危险/错误颜色
COLOR_NEUTRAL = "#34495e"     # 中性色
COLOR_BACKGROUND = "#f5f5f7"  # 背景色
COLOR_PREVIEW_BG = "#f9f9f9"  # 预览区背景色

# 深色主题颜色配置
DARK_COLOR_PRIMARY = "#3498db"     # 主要颜色 (亮蓝色)
DARK_COLOR_SUCCESS = "#2ecc71"     # 成功/确认颜色 (亮绿色)
DARK_COLOR_WARNING = "#f39c12"     # 警告颜色 (亮橙色)
DARK_COLOR_DANGER = "#e74c3c"      # 危险/错误颜色 (亮红色)
DARK_COLOR_NEUTRAL = "#ecf0f1"     # 中性色 (浅灰白文本)
DARK_COLOR_BACKGROUND = "#1a1a2e"  # 背景色 (深蓝黑色)
DARK_COLOR_PREVIEW_BG = "#2a2a42"  # 预览区背景色 (深紫蓝色)

# UI配置
UI_FONT = "微软雅黑"
UI_FONT_SIZE = 10
UI_FONT_SIZE_SMALL = 9
UI_FONT_SIZE_LARGE = 12
UI_FONT_SIZE_TITLE = 14
UI_FONT_BOLD = (UI_FONT, UI_FONT_SIZE, "bold")
UI_FONT_NORMAL = (UI_FONT, UI_FONT_SIZE)
UI_FONT_LARGE = (UI_FONT, UI_FONT_SIZE_LARGE)
UI_FONT_TITLE = (UI_FONT, UI_FONT_SIZE_TITLE, "bold")
UI_FONT_SMALL = (UI_FONT, UI_FONT_SIZE_SMALL)

# 时间格式
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
FILENAME_TIME_FORMAT = "%Y%m%d_%H%M%S"

# 定时提醒配置
DEFAULT_REMINDER_TIME = "17:30"  # 默认提醒时间
REMINDER_MESSAGE = "该记录今天的工作了！"
REMINDER_SOUND_ENABLED = True
INTERVAL_REMINDER_MINUTES = 25  # 间隔提醒时间（分钟）
INTERVAL_REMINDER_MESSAGE = "已工作25分钟，建议休息一下并记录工作内容"

# 表格显示配置
TABLE_COLUMNS = [
    {"id": "id", "text": "ID", "width": 50},
    {"id": "task_name", "text": "项目/事务", "width": 200},
    {"id": "timestamp", "text": "时间", "width": 150},
]