"""
截图工具模块 - 处理截图相关的功能
"""

import os
import time
import datetime
import pyautogui
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
from tkinter import messagebox
from typing import Tuple, Optional

from src.config import SCREENSHOT_DIR, FILENAME_TIME_FORMAT
from src.utils.data_manager import DataManager
from src.utils.config_manager import default_config_manager

# 创建数据管理器实例
data_manager = DataManager()


def take_fullscreen_screenshot(window):
    """
    捕获全屏截图
    
    Args:
        window: 主窗口对象，用于临时最小化
        
    Returns:
        PIL.Image: 截图对象
    """
    # 最小化窗口以便截图不包含本应用
    window.iconify()
    window.update()  # 强制刷新
    time.sleep(1.0)  # 等待更久，确保窗口消失
    
    # 捕获全屏截图
    screenshot = pyautogui.screenshot()
    
    # 恢复窗口
    window.deiconify()
    
    return screenshot


class RegionSelector:
    """区域选择器类，用于选择屏幕区域进行截图"""
    
    def __init__(self, parent_window):
        """初始化区域选择器
        
        Args:
            parent_window: 父窗口对象
        """
        self.parent = parent_window
        self.parent.withdraw()  # 隐藏父窗口
        self.parent.update()    # 强制刷新
        time.sleep(1.0)        # 等待更久，确保窗口消失
        
        # 截图区域坐标
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.is_selecting = False
        self.screenshot = None
        
        # 创建全屏窗口
        self.root = tk.Toplevel(self.parent)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # 设置透明度
        self.root.attributes('-topmost', True)
        
        # 防止窗口管理器装饰
        self.root.overrideredirect(True)
        
        # 获取全屏截图用于背景
        self.background_image = pyautogui.screenshot()
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        
        # 创建画布
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 显示截图作为背景
        self.canvas.create_image(0, 0, image=self.background_photo, anchor=tk.NW)
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # 绑定键盘事件
        self.root.bind("<Escape>", self.on_escape)
        
        # 显示提示文本
        self.canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            30,
            text="请拖动鼠标选择截图区域，按ESC取消",
            fill="black",
            font=("微软雅黑", 14, "bold")
        )
        
        # 矩形ID
        self.rect_id = None
        self.info_id = None
    
    def on_mouse_down(self, event):
        """鼠标按下事件处理
        
        Args:
            event: 鼠标事件对象
        """
        self.is_selecting = True
        self.start_x = event.x
        self.start_y = event.y
        
        # 创建矩形
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=5
        )
        
        # 创建信息文本
        self.info_id = self.canvas.create_text(
            self.start_x, self.start_y - 10,
            text="0 x 0",
            fill="red",
            font=("微软雅黑", 10)
        )
    
    def on_mouse_move(self, event):
        """鼠标移动事件处理
        
        Args:
            event: 鼠标事件对象
        """
        if self.is_selecting:
            self.end_x = event.x
            self.end_y = event.y
            
            # 更新矩形
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, self.end_x, self.end_y)
            
            # 计算宽度和高度
            width = abs(self.end_x - self.start_x)
            height = abs(self.end_y - self.start_y)
            
            # 更新信息文本
            self.canvas.itemconfig(self.info_id, text=f"{width} x {height}")
            self.canvas.coords(self.info_id, min(self.start_x, self.end_x) + width // 2, min(self.start_y, self.end_y) - 10)
    
    def on_mouse_up(self, event):
        """鼠标释放事件处理
        
        Args:
            event: 鼠标事件对象
        """
        if self.is_selecting:
            self.is_selecting = False
            self.end_x = event.x
            self.end_y = event.y
            
            # 获取选择区域的截图
            x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
            x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)
            
            if (x2 - x1) > 10 and (y2 - y1) > 10:  # 确保选择的区域足够大
                # 从背景图像截取选定区域
                self.screenshot = self.background_image.crop((x1, y1, x2, y2))
                self.root.destroy()
            else:
                messagebox.showinfo("提示", "选择的区域太小，请重新选择")
                self.canvas.delete(self.rect_id)
                self.canvas.delete(self.info_id)
    
    def on_escape(self, event):
        """ESC键事件处理
        
        Args:
            event: 键盘事件对象
        """
        self.root.destroy()
    
    def get_screenshot(self):
        """获取截图
        
        Returns:
            PIL.Image: 截图对象
        """
        return self.screenshot


def take_region_screenshot(window):
    """
    捕获选定区域的截图
    
    Args:
        window: 主窗口对象
        
    Returns:
        PIL.Image: 截图对象或None（如果用户取消）
    """
    selector = RegionSelector(window)
    window.wait_window(selector.root)  # 等待选择窗口关闭
    
    # 恢复主窗口
    window.deiconify()
    
    # 返回截图
    return selector.get_screenshot()


def resize_image_for_preview(image, frame_width, frame_height, padding=10):
    """
    调整图像大小以适应预览区域，保持纵横比
    
    Args:
        image: PIL.Image对象
        frame_width: 预览框架宽度
        frame_height: 预览框架高度
        padding: 边距大小
        
    Returns:
        PIL.ImageTk.PhotoImage: 调整大小后的图像对象，用于Tkinter显示
    """
    if not image:
        return None
        
    # 确保尺寸至少为1像素
    preview_width = max(1, frame_width - padding)
    preview_height = max(1, frame_height - padding)
    
    # 调整图像大小以适应预览区域，保持纵横比
    img_width, img_height = image.size
    ratio = min(preview_width/max(1, img_width), preview_height/max(1, img_height))
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)
    
    resized_img = image.resize((new_width, new_height), Image.LANCZOS)
    return ImageTk.PhotoImage(resized_img)


def save_screenshot(image, task_name, notes="") -> Tuple[bool, str]:
    """
    保存截图到文件并记录到数据库
    
    Args:
        image: PIL.Image对象
        task_name: 任务/项目名称
        notes: 附加说明
        
    Returns:
        tuple: (成功标志, 消息或文件路径)
    """
    if not image:
        return False, "没有可保存的截图"
    
    if not task_name.strip():
        return False, "请输入项目/事务名称"
    
    try:
        # 从配置管理器获取保存路径
        config_manager = default_config_manager
        use_custom_path = config_manager.get_value("files", "use_custom_path", False)
        
        if use_custom_path:
            # 使用用户自定义的保存路径
            save_dir = config_manager.get_value("files", "screenshot_save_path", SCREENSHOT_DIR)
            # 检查路径是否为空或无效
            if not save_dir or not isinstance(save_dir, str):
                print(f"自定义路径无效，使用默认路径: {SCREENSHOT_DIR}")
                save_dir = SCREENSHOT_DIR
        else:
            # 使用默认的保存路径
            save_dir = SCREENSHOT_DIR
        
        # 标准化路径
        save_dir = os.path.normpath(save_dir)
        print(f"使用保存路径: {save_dir}")
        
        # 确保保存目录存在
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir, exist_ok=True)
                print(f"已创建保存目录: {save_dir}")
            except Exception as e:
                print(f"创建保存目录失败: {e}")
                # 如果创建失败，尝试使用默认目录
                save_dir = os.path.join(os.path.expanduser("~"), "留痕软件_截图")
                print(f"尝试使用备选目录: {save_dir}")
                os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件名：时间_项目名称.png
        timestamp = datetime.datetime.now().strftime(FILENAME_TIME_FORMAT)
        # 替换文件名中不允许的字符
        safe_task = "".join([c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in task_name])
        filename = f"{timestamp}_{safe_task}.png"
        filepath = os.path.join(save_dir, filename)
        
        # 确保文件名不超过系统限制（通常Windows为260个字符）
        if len(filepath) > 250:
            # 截断项目名称
            filepath = os.path.join(save_dir, f"{timestamp}_截图.png")
        
        # 获取截图质量
        quality = config_manager.get_value("ui", "screenshot_quality", 90)
        
        # 保存截图
        print(f"保存截图到: {filepath}，质量: {quality}")
        image.save(filepath, quality=quality)
        
        # 添加记录到数据管理器
        data_manager.add_record(task_name, filepath, notes)
        
        return True, filepath
    except Exception as e:
        error_msg = f"保存截图时发生错误: {str(e)}"
        print(error_msg)
        # 尝试保存到用户目录作为最后的备选
        try:
            backup_dir = os.path.join(os.path.expanduser("~"), "留痕软件_截图")
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"{datetime.datetime.now().strftime(FILENAME_TIME_FORMAT)}_备份.png")
            image.save(backup_path)
            return False, f"{error_msg}\n已创建备份: {backup_path}"
        except Exception as backup_error:
            return False, f"{error_msg}\n备份也失败: {str(backup_error)}"


def load_image_from_path(image_path) -> Optional[Image.Image]:
    """
    从文件路径加载图像
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        PIL.Image: 图像对象，如果加载失败则返回None
    """
    try:
        # 尝试直接加载
        if os.path.exists(image_path):
            return Image.open(image_path)
        
        # 如果失败，尝试转换路径格式后加载
        alt_path = image_path.replace('/', '\\') if '/' in image_path else image_path.replace('\\', '/')
        if os.path.exists(alt_path):
            return Image.open(alt_path)
        
        return None
    except Exception as e:
        print(f"加载图片失败: {e}")
        return None