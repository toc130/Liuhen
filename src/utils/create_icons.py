"""
图标生成工具 - 为留痕软件创建图标
"""

import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告: 未安装PIL库，请使用以下命令安装: pip install pillow")

# 确保src目录在Python路径中
script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, script_dir)

try:
    from src.config import (
        COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, 
        COLOR_DANGER, COLOR_NEUTRAL, UI_FONT
    )
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("错误: 无法导入配置，请确保运行目录正确")
    
    # 使用默认颜色
    COLOR_PRIMARY = "#3498db"
    COLOR_SUCCESS = "#2ecc71"
    COLOR_WARNING = "#f39c12"
    COLOR_DANGER = "#e74c3c"
    COLOR_NEUTRAL = "#34495e"
    UI_FONT = "微软雅黑"


def create_app_icon(output_path, size=128):
    """
    创建应用程序图标
    
    Args:
        output_path: 输出路径
        size: 图标大小
    """
    if not PIL_AVAILABLE:
        return False
        
    try:
        # 创建一个新的图像
        image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 计算圆的半径和位置
        radius = size // 2 - 4
        center = size // 2
        
        # 绘制圆形背景
        draw.ellipse((center - radius, center - radius, center + radius, center + radius), fill=COLOR_PRIMARY)
        
        # 创建羽毛笔图标
        pen_color = 'white'
        pen_width = radius // 2
        pen_height = radius * 1.5
        
        # 羽毛笔位置
        pen_left = center - pen_width // 2
        pen_top = center - pen_height // 2 - 5
        
        # 绘制羽毛笔主体
        draw.polygon([
            (pen_left, pen_top + pen_height * 0.8),
            (pen_left + pen_width, pen_top + pen_height * 0.8),
            (pen_left + pen_width, pen_top + pen_height),
            (pen_left, pen_top + pen_height)
        ], fill=pen_color)
        
        # 绘制羽毛笔顶部
        draw.polygon([
            (pen_left, pen_top + pen_height * 0.8),
            (pen_left + pen_width, pen_top + pen_height * 0.8),
            (pen_left + pen_width // 2, pen_top)
        ], fill=pen_color)
        
        # 添加羽毛笔细节
        detail_color = COLOR_NEUTRAL
        detail_width = pen_width // 4
        
        draw.line(
            [(pen_left + pen_width // 2, pen_top + 5), 
             (pen_left + pen_width // 2, pen_top + pen_height * 0.7)], 
            fill=detail_color, width=2
        )
        
        # 保存图标
        image.save(output_path)
        print(f"应用图标已创建: {output_path}")
        return True
    except Exception as e:
        print(f"创建应用图标时出错: {str(e)}")
        return False

def create_screenshot_icon(output_path, size=64):
    """
    创建截图按钮图标
    
    Args:
        output_path: 输出路径
        size: 图标大小
    """
    if not PIL_AVAILABLE:
        return False
        
    try:
        # 创建一个新的图像
        image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制相机图标
        margin = size // 8
        width = size - 2 * margin
        height = width * 3 // 4
        
        # 相机主体
        draw.rectangle(
            (margin, margin + height // 3, margin + width, margin + height),
            fill=COLOR_PRIMARY
        )
        
        # 相机顶部凸起部分
        draw.rectangle(
            (margin + width // 3, margin, margin + width * 2 // 3, margin + height // 3),
            fill=COLOR_PRIMARY
        )
        
        # 相机镜头
        lens_margin = size // 4
        lens_size = size // 2
        draw.ellipse(
            (lens_margin, lens_margin + height // 6, lens_margin + lens_size, lens_margin + lens_size + height // 6),
            outline='white',
            width=2
        )
        
        # 相机闪光灯
        flash_size = size // 10
        draw.rectangle(
            (margin + width - flash_size * 2, margin + height // 6, 
             margin + width - flash_size, margin + height // 6 + flash_size),
            fill='white'
        )
        
        # 保存图标
        image.save(output_path)
        print(f"截图图标已创建: {output_path}")
        return True
    except Exception as e:
        print(f"创建截图图标时出错: {str(e)}")
        return False

def create_save_icon(output_path, size=64):
    """
    创建保存按钮图标
    
    Args:
        output_path: 输出路径
        size: 图标大小
    """
    if not PIL_AVAILABLE:
        return False
        
    try:
        # 创建一个新的图像
        image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制磁盘图标
        margin = size // 8
        width = size - 2 * margin
        height = width
        
        # 磁盘主体
        draw.rectangle(
            (margin, margin, margin + width, margin + height),
            fill=COLOR_SUCCESS
        )
        
        # 磁盘中心孔
        center_size = width // 3
        center_margin = margin + (width - center_size) // 2
        draw.ellipse(
            (center_margin, center_margin, center_margin + center_size, center_margin + center_size),
            fill='white'
        )
        
        # 磁盘标签区域
        label_height = height // 4
        draw.rectangle(
            (margin + width // 4, margin + height // 8, 
             margin + width * 3 // 4, margin + height // 8 + label_height),
            fill='white'
        )
        
        # 保存图标
        image.save(output_path)
        print(f"保存图标已创建: {output_path}")
        return True
    except Exception as e:
        print(f"创建保存图标时出错: {str(e)}")
        return False

def create_clear_icon(output_path, size=64):
    """
    创建清除按钮图标
    
    Args:
        output_path: 输出路径
        size: 图标大小
    """
    if not PIL_AVAILABLE:
        return False
        
    try:
        # 创建一个新的图像
        image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制垃圾桶图标
        margin = size // 8
        width = size - 2 * margin
        height = width * 5 // 4
        
        # 垃圾桶顶部
        top_height = height // 6
        draw.rectangle(
            (margin, margin, margin + width, margin + top_height),
            fill=COLOR_DANGER
        )
        
        # 垃圾桶手柄
        handle_width = width // 3
        handle_margin = margin + (width - handle_width) // 2
        draw.rectangle(
            (handle_margin, margin - top_height // 2, 
             handle_margin + handle_width, margin),
            fill=COLOR_DANGER
        )
        
        # 垃圾桶主体
        draw.rectangle(
            (margin + width // 8, margin + top_height, 
             margin + width - width // 8, margin + height),
            fill=COLOR_DANGER
        )
        
        # 垃圾桶条纹
        stripe_width = 2
        for i in range(3):
            x = margin + width // 4 + i * width // 4
            draw.line(
                [(x, margin + top_height + top_height), 
                 (x, margin + height - top_height)], 
                fill='white', width=stripe_width
            )
        
        # 保存图标
        image.save(output_path)
        print(f"清除图标已创建: {output_path}")
        return True
    except Exception as e:
        print(f"创建清除图标时出错: {str(e)}")
        return False

def create_query_icon(output_path, size=64):
    """
    创建查询按钮图标
    
    Args:
        output_path: 输出路径
        size: 图标大小
    """
    if not PIL_AVAILABLE:
        return False
        
    try:
        # 创建一个新的图像
        image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制放大镜图标
        margin = size // 8
        
        # 放大镜圆环
        radius = size // 3
        center_x = margin + radius
        center_y = margin + radius
        draw.ellipse(
            (margin, margin, margin + radius * 2, margin + radius * 2),
            outline=COLOR_PRIMARY,
            width=3
        )
        
        # 放大镜手柄
        handle_width = 3
        handle_length = size // 3
        draw.line(
            [(center_x + radius * 0.7, center_y + radius * 0.7), 
             (center_x + radius * 0.7 + handle_length, center_y + radius * 0.7 + handle_length)], 
            fill=COLOR_PRIMARY, width=handle_width
        )
        
        # 保存图标
        image.save(output_path)
        print(f"查询图标已创建: {output_path}")
        return True
    except Exception as e:
        print(f"创建查询图标时出错: {str(e)}")
        return False

def create_reminder_icon(output_path, size=64):
    """
    创建提醒按钮图标
    
    Args:
        output_path: 输出路径
        size: 图标大小
    """
    if not PIL_AVAILABLE:
        return False
        
    try:
        # 创建一个新的图像
        image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制闹钟图标
        margin = size // 8
        
        # 闹钟主体
        radius = size // 3
        center_x = size // 2
        center_y = size // 2
        draw.ellipse(
            (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
            outline=COLOR_WARNING,
            width=3
        )
        
        # 闹钟顶部
        bell_width = radius
        bell_height = radius // 2
        draw.arc(
            (center_x - bell_width // 2, center_y - radius - bell_height, 
             center_x + bell_width // 2, center_y - radius + bell_height),
            180, 0,  # 从180度到0度的弧（下半圆）
            fill=COLOR_WARNING,
            width=2
        )
        
        # 闹钟指针
        draw.line(
            [(center_x, center_y), (center_x, center_y - radius * 0.6)], 
            fill=COLOR_WARNING, width=2
        )
        draw.line(
            [(center_x, center_y), (center_x + radius * 0.4, center_y)], 
            fill=COLOR_WARNING, width=2
        )
        
        # 闹钟底部支架
        draw.line(
            [(center_x - radius * 0.5, center_y + radius), 
             (center_x - radius, center_y + radius * 1.3)], 
            fill=COLOR_WARNING, width=2
        )
        draw.line(
            [(center_x + radius * 0.5, center_y + radius), 
             (center_x + radius, center_y + radius * 1.3)], 
            fill=COLOR_WARNING, width=2
        )
        
        # 保存图标
        image.save(output_path)
        print(f"提醒图标已创建: {output_path}")
        return True
    except Exception as e:
        print(f"创建提醒图标时出错: {str(e)}")
        return False

def create_interval_icon(output_path, size=64):
    """
    创建间隔提醒按钮图标
    
    Args:
        output_path: 输出路径
        size: 图标大小
    """
    if not PIL_AVAILABLE:
        return False
        
    try:
        # 创建一个新的图像
        image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制时钟图标
        margin = size // 8
        
        # 时钟主体
        radius = size // 3
        center_x = size // 2
        center_y = size // 2
        draw.ellipse(
            (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
            outline=COLOR_NEUTRAL,
            width=3
        )
        
        # 刻度 (简化版)
        for i in range(12):
            angle = i * 30  # 每小时30度
            inner_radius = radius * 0.8
            outer_radius = radius * 0.9 if i % 3 == 0 else radius * 0.85
            
            rad = angle * 3.14159 / 180
            x1 = center_x + inner_radius * math.cos(rad - math.pi/2)  # -pi/2 因为0度在3点钟位置
            y1 = center_y + inner_radius * math.sin(rad - math.pi/2)
            x2 = center_x + outer_radius * math.cos(rad - math.pi/2)
            y2 = center_y + outer_radius * math.sin(rad - math.pi/2)
            
            draw.line([(x1, y1), (x2, y2)], fill=COLOR_NEUTRAL, width=2)
        
        # 时钟指针
        # 时针 (指向8点钟方向)
        hour_angle = 240  # 8小时 = 240度
        hour_rad = hour_angle * 3.14159 / 180
        hour_length = radius * 0.5
        hour_x = center_x + hour_length * math.cos(hour_rad - math.pi/2)
        hour_y = center_y + hour_length * math.sin(hour_rad - math.pi/2)
        draw.line([(center_x, center_y), (hour_x, hour_y)], fill=COLOR_NEUTRAL, width=3)
        
        # 分针 (指向5点钟方向)
        minute_angle = 150  # 5 * 30 = 150度
        minute_rad = minute_angle * 3.14159 / 180
        minute_length = radius * 0.7
        minute_x = center_x + minute_length * math.cos(minute_rad - math.pi/2)
        minute_y = center_y + minute_length * math.sin(minute_rad - math.pi/2)
        draw.line([(center_x, center_y), (minute_x, minute_y)], fill=COLOR_NEUTRAL, width=2)
        
        # 循环箭头 (简化版)
        arrow_radius = radius * 1.4
        arrow_start = 120  # 开始角度
        arrow_end = 300    # 结束角度
        
        # 绘制箭头弧
        for i in range(arrow_start, arrow_end, 5):
            rad1 = i * 3.14159 / 180
            rad2 = (i + 5) * 3.14159 / 180
            x1 = center_x + arrow_radius * math.cos(rad1 - math.pi/2)
            y1 = center_y + arrow_radius * math.sin(rad1 - math.pi/2)
            x2 = center_x + arrow_radius * math.cos(rad2 - math.pi/2)
            y2 = center_y + arrow_radius * math.sin(rad2 - math.pi/2)
            
            draw.line([(x1, y1), (x2, y2)], fill=COLOR_WARNING, width=4)
        
        # 箭头头部
        arrow_head_size = size // 10
        arrow_head_angle = 120  # 箭头位置
        arrow_head_rad = arrow_head_angle * 3.14159 / 180
        arrow_head_x = center_x + arrow_radius * math.cos(arrow_head_rad - math.pi/2)
        arrow_head_y = center_y + arrow_radius * math.sin(arrow_head_rad - math.pi/2)
        
        # 绘制简化的箭头头部
        draw.polygon([
            (arrow_head_x, arrow_head_y),
            (arrow_head_x - arrow_head_size, arrow_head_y),
            (arrow_head_x - arrow_head_size//2, arrow_head_y - arrow_head_size)
        ], fill=COLOR_WARNING)
        
        # 保存图标
        image.save(output_path)
        print(f"间隔提醒图标已创建: {output_path}")
        return True
    except Exception as e:
        print(f"创建间隔提醒图标时出错: {str(e)}")
        return False

def main():
    """主函数"""
    if not PIL_AVAILABLE:
        print("错误: 未安装PIL库，无法创建图标")
        print("请使用以下命令安装: pip install pillow")
        return
    
    print("开始创建图标...")
    
    try:
        import math  # 添加数学库，用于计算角度
        
        # 获取图标目录
        icons_dir = os.path.join(script_dir, "assets", "icons")
        
        # 确保图标目录存在
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)
            print(f"创建图标目录: {icons_dir}")
        
        # 创建应用图标
        create_app_icon(os.path.join(icons_dir, "app_icon.png"))
        
        # 尝试创建ico格式图标
        try:
            create_app_icon(os.path.join(icons_dir, "app_icon.ico"))
        except Exception as e:
            print(f"无法创建ICO格式图标: {str(e)}，将使用PNG替代")
        
        # 创建按钮图标
        create_screenshot_icon(os.path.join(icons_dir, "screenshot.png"))
        create_save_icon(os.path.join(icons_dir, "save.png"))
        create_clear_icon(os.path.join(icons_dir, "clear.png"))
        create_query_icon(os.path.join(icons_dir, "query.png"))
        create_reminder_icon(os.path.join(icons_dir, "reminder.png"))
        create_interval_icon(os.path.join(icons_dir, "interval.png"))
        
        print("所有图标创建完成！")
    except Exception as e:
        print(f"创建图标时发生错误: {str(e)}")

if __name__ == "__main__":
    main() 