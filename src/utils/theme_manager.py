"""
主题管理器模块 - 负责应用级的主题管理
"""

import os
import json
import tkinter as tk
from tkinter import ttk

# 导入应用配置
from src.config import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, 
    COLOR_NEUTRAL, COLOR_BACKGROUND, COLOR_PREVIEW_BG,
    DARK_COLOR_PRIMARY, DARK_COLOR_SUCCESS, DARK_COLOR_WARNING, 
    DARK_COLOR_DANGER, DARK_COLOR_NEUTRAL, DARK_COLOR_BACKGROUND, 
    DARK_COLOR_PREVIEW_BG
)

class ThemeManager:
    """
    主题管理器类 - 单例模式
    集中管理应用程序的主题设置和颜色方案
    """
    
    _instance = None  # 单例实例
    
    @classmethod
    def get_instance(cls):
        """获取ThemeManager单例实例"""
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance
    
    def __init__(self):
        """初始化主题管理器"""
        if ThemeManager._instance is not None:
            raise Exception("ThemeManager是单例类，请使用get_instance()方法获取实例")
        
        # 注册的窗口列表
        self.windows = []
        
        # 主题状态
        self.is_dark_mode = False
        
        # 当前主题颜色
        self.theme_colors = {}
        
        # 加载保存的主题设置
        self.load_theme_settings()
        
        # 初始化主题颜色
        self.update_theme_colors()
    
    def register_window(self, window):
        """注册窗口到主题管理器
        
        Args:
            window: 需要管理的窗口实例，必须实现_update_theme方法
        """
        if window not in self.windows:
            # 仅保存窗口的弱引用，防止内存泄漏
            self.windows.append(window)
    
    def unregister_window(self, window):
        """从主题管理器中注销窗口
        
        Args:
            window: 要注销的窗口实例
        """
        if window in self.windows:
            self.windows.remove(window)
    
    def toggle_theme(self):
        """切换主题并通知所有窗口"""
        self.is_dark_mode = not self.is_dark_mode
        self.update_theme_colors()
        self.save_theme_settings()
        self.notify_all_windows()
        return self.is_dark_mode
    
    def set_theme(self, is_dark_mode):
        """设置指定的主题
        
        Args:
            is_dark_mode: 是否使用深色主题
        """
        if self.is_dark_mode == is_dark_mode:
            return False  # 主题未变化
            
        self.is_dark_mode = is_dark_mode
        self.update_theme_colors()
        self.save_theme_settings()
        self.notify_all_windows()
        return True
    
    def update_theme_colors(self):
        """更新主题颜色字典"""
        if self.is_dark_mode:
            self.theme_colors = {
                "primary": DARK_COLOR_PRIMARY,
                "success": DARK_COLOR_SUCCESS,
                "warning": DARK_COLOR_WARNING,
                "danger": DARK_COLOR_DANGER, 
                "neutral": DARK_COLOR_NEUTRAL,
                "background": DARK_COLOR_BACKGROUND,
                "preview_bg": DARK_COLOR_PREVIEW_BG,
                
                # 扩展颜色定义
                "window_bg": DARK_COLOR_BACKGROUND,
                "frame_bg": "#252540",
                "text_primary": DARK_COLOR_NEUTRAL,
                "text_secondary": "#aaaaaa",
                "button_bg": "#333350",
                "button_hover": "#444470",
                "button_active": "#555590",
                "input_bg": "#333350",
                "input_border": "#555555",
                "table_header_bg": "#333350",
                "table_row_even": "#252540",
                "table_row_odd": "#2a2a45",
                "table_border": "#444444",
                "table_selected": "#3a3a5e",
                "border": "#666666",
                "tooltip_bg": "#ecf0f1",
                "tooltip_text": "#1a1a2e",
            }
        else:
            self.theme_colors = {
                "primary": COLOR_PRIMARY,
                "success": COLOR_SUCCESS,
                "warning": COLOR_WARNING,
                "danger": COLOR_DANGER,
                "neutral": COLOR_NEUTRAL,
                "background": COLOR_BACKGROUND,
                "preview_bg": COLOR_PREVIEW_BG,
                
                # 扩展颜色定义
                "window_bg": COLOR_BACKGROUND,
                "frame_bg": "#ffffff",
                "text_primary": COLOR_NEUTRAL,
                "text_secondary": "#888888",
                "button_bg": "#f0f0f0",
                "button_hover": "#e0e0e0",
                "button_active": "#d0d0d0",
                "input_bg": "#ffffff",
                "input_border": "#cccccc",
                "table_header_bg": "#f0f0f0",
                "table_row_even": "#f9f9f9",
                "table_row_odd": "#ffffff",
                "table_border": "#eeeeee",
                "table_selected": "#e6f7ff",
                "border": "#cccccc",
                "tooltip_bg": "#333333",
                "tooltip_text": "#ffffff",
            }
    
    def notify_all_windows(self):
        """通知所有注册的窗口更新主题"""
        windows_to_remove = []
        
        for window in self.windows:
            try:
                if hasattr(window, '_update_theme'):
                    window._update_theme(self.is_dark_mode)
            except Exception as e:
                print(f"更新窗口主题失败: {e}")
                # 如果窗口已不存在，加入待删除列表
                windows_to_remove.append(window)
        
        # 删除不可用的窗口引用
        for window in windows_to_remove:
            self.windows.remove(window)
    
    def get_config_path(self):
        """获取配置文件路径"""
        # 使用用户主目录下的隐藏文件夹存储配置
        config_dir = os.path.join(os.path.expanduser("~"), ".liuhen")
        
        # 确保目录存在
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        return os.path.join(config_dir, "theme_config.json")
    
    def save_theme_settings(self):
        """保存主题设置到配置文件"""
        try:
            config_path = self.get_config_path()
            
            # 导入datetime模块
            import datetime
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "is_dark_mode": self.is_dark_mode,
                    "last_updated": datetime.datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
                
            print(f"主题设置已保存到: {config_path}")
            return True
        except Exception as e:
            print(f"保存主题设置失败: {e}")
            return False
    
    def load_theme_settings(self):
        """从配置文件加载主题设置"""
        try:
            config_path = self.get_config_path()
            
            if not os.path.exists(config_path):
                print("没有找到主题配置文件，使用默认主题")
                # 尝试检测系统主题
                self.is_dark_mode = self.detect_system_theme()
                return False
                
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.is_dark_mode = config.get("is_dark_mode", False)
                
            print(f"已加载主题设置，当前使用{'深色' if self.is_dark_mode else '浅色'}主题")
            return True
        except Exception as e:
            print(f"加载主题设置失败: {e}")
            # 出错时默认使用浅色主题
            self.is_dark_mode = False
            return False
    
    def detect_system_theme(self):
        """
        检测系统主题设置
        
        Returns:
            bool: 如果系统使用深色主题则返回True，否则返回False
        """
        try:
            # Windows系统
            if os.name == 'nt':
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return value == 0  # 0表示使用深色主题
                except Exception as e:
                    print(f"检测Windows主题失败: {e}")
                    return False
                
            # macOS系统
            elif os.name == 'posix' and hasattr(os, 'uname') and os.uname().sysname == 'Darwin':
                try:
                    import subprocess
                    result = subprocess.run(
                        ['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                        capture_output=True, 
                        text=True
                    )
                    return result.stdout.strip() == 'Dark'
                except Exception as e:
                    print(f"检测macOS主题失败: {e}")
                    return False
                
            # Linux系统 (GNOME)
            elif os.name == 'posix':
                try:
                    import subprocess
                    result = subprocess.run(
                        ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], 
                        capture_output=True, 
                        text=True
                    )
                    return 'dark' in result.stdout.lower()
                except Exception as e:
                    print(f"检测Linux主题失败: {e}")
                    return False
        except Exception as e:
            print(f"检测系统主题失败: {e}")
        
        # 默认返回浅色主题
        return False
    
    def apply_themed_styles(self, style=None):
        """
        应用主题化样式到ttk Style对象
        
        Args:
            style: ttk.Style实例，如果为None则创建新实例
        
        Returns:
            ttk.Style: 配置好的样式对象
        """
        if style is None:
            style = ttk.Style()
        
        # 使用clam主题作为基础
        style.theme_use('clam')
        
        # 配置颜色映射
        # 获取当前主题颜色
        colors = self.theme_colors
        
        # 按钮样式
        style.configure("TButton", 
                      background=colors["button_bg"],
                      foreground=colors["text_primary"])
        
        style.map("TButton",
                background=[('active', colors["button_active"]), ('pressed', colors["button_active"])],
                foreground=[('active', colors["text_primary"])])
        
        # 主要按钮样式
        style.configure("Primary.TButton", 
                      background=colors["primary"],
                      foreground="#ffffff")
        
        style.map("Primary.TButton",
                background=[('active', colors["primary"]), ('pressed', colors["primary"])])
        
        # 成功按钮样式
        style.configure("Success.TButton", 
                      background=colors["success"],
                      foreground="#ffffff")
        
        style.map("Success.TButton",
                background=[('active', colors["success"]), ('pressed', colors["success"])])
        
        # 框架样式
        style.configure("TFrame", background=colors["frame_bg"])
        style.configure("TLabelframe", background=colors["frame_bg"])
        style.configure("TLabelframe.Label", background=colors["frame_bg"], foreground=colors["text_primary"])
        
        # 标签样式
        style.configure("TLabel", background=colors["frame_bg"], foreground=colors["text_primary"])
        
        # 输入框样式
        style.configure("TEntry", 
                      fieldbackground=colors["input_bg"],
                      foreground=colors["text_primary"],
                      background=colors["input_border"])
        
        # 表格样式
        style.configure("Treeview", 
                      background=colors["table_row_odd"],
                      fieldbackground=colors["table_row_odd"],
                      foreground=colors["text_primary"])
        
        style.configure("Treeview.Heading", 
                      background=colors["table_header_bg"],
                      foreground=colors["text_primary"],
                      relief="raised")
        
        style.map("Treeview",
                background=[('selected', colors["table_selected"])],
                foreground=[('selected', colors["text_primary"])])
        
        # 分隔线样式
        style.configure("TSeparator", background=colors["border"])
        
        # 预览标签样式
        style.configure("Preview.TLabel",
                      background=colors["preview_bg"],
                      foreground=colors["text_secondary"])
        
        # 滚动条样式
        style.configure("Vertical.TScrollbar", 
                      background=colors["button_bg"],
                      arrowcolor=colors["text_primary"],
                      bordercolor=colors["border"],
                      troughcolor=colors["frame_bg"])
        
        return style


# 创建默认实例
default_theme_manager = ThemeManager.get_instance()


# 提供一个ThemedWindow基类，简化窗口的主题管理
class ThemedWindow(tk.Toplevel):
    """支持主题切换的窗口基类"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, **kwargs)
        self.title(title)
        
        # 获取主题管理器
        self.theme_manager = ThemeManager.get_instance()
        
        # 注册到主题管理器
        self.theme_manager.register_window(self)
        
        # 获取当前主题状态
        self.is_dark_mode = self.theme_manager.is_dark_mode
        self.theme_colors = self.theme_manager.theme_colors
        
        # 设置窗口背景色
        self.configure(bg=self.theme_colors["window_bg"])
        
        # 窗口关闭时解除注册
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _update_theme(self, is_dark_mode):
        """
        更新主题 - 子类应重写此方法以实现自定义主题更新逻辑
        
        Args:
            is_dark_mode: 是否使用深色主题
        """
        self.is_dark_mode = is_dark_mode
        self.theme_colors = self.theme_manager.theme_colors
        
        # 更新窗口背景色
        self.configure(bg=self.theme_colors["window_bg"])
    
    def _on_close(self):
        """窗口关闭时的处理"""
        # 从主题管理器取消注册
        self.theme_manager.unregister_window(self)
        self.destroy()
    
    def create_themed_style(self):
        """创建并返回主题化的样式对象"""
        style = ttk.Style(self)
        return self.theme_manager.apply_themed_styles(style) 