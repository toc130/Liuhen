"""
主应用GUI模块 - 实现留痕软件的图形界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import threading
from PIL import Image, ImageTk
import time

from src.config import (
    APP_NAME, APP_WINDOW_SIZE, 
    UI_FONT_BOLD, UI_FONT_NORMAL, UI_FONT_TITLE, UI_FONT_LARGE, UI_FONT_SMALL,
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, 
    COLOR_NEUTRAL, COLOR_BACKGROUND, COLOR_PREVIEW_BG,
    DEFAULT_REMINDER_TIME, REMINDER_MESSAGE, REMINDER_SOUND_ENABLED,
    INTERVAL_REMINDER_MINUTES, INTERVAL_REMINDER_MESSAGE
)
from src.utils.screenshot import take_fullscreen_screenshot, resize_image_for_preview, save_screenshot, take_region_screenshot
from src.utils.time_utils import get_current_time_str, parse_time_string, calculate_next_reminder_time, time_until_next_reminder, format_time_delta, calculate_next_interval_reminder
from src.gui.records_view import RecordsView
from src.gui.editor import ScreenshotEditor  # 添加编辑器导入


class ActivityTrackerApp:
    """
    留痕软件主应用类
    """
    def __init__(self, root):
        """
        初始化应用
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry(APP_WINDOW_SIZE)
        self.root.resizable(True, True)
        self.root.configure(background=COLOR_BACKGROUND)
        
        # 加载图标
        self.load_icons()
        
        # 设置样式
        self._setup_styles()
        
        # 创建UI组件
        self._create_widgets()
        
        # 截图相关变量
        self.current_screenshot = None
        self.screenshot_preview = None
        
        # 定时提醒相关变量
        self.reminder_active = False
        self.reminder_thread = None
        self.next_reminder_time = None
        
        # 间隔提醒相关变量
        self.interval_reminder_active = False
        self.interval_reminder_thread = None
        self.next_interval_time = None
        
        # 启动时间更新
        self.update_time()
        
        # 绑定窗口大小改变事件
        self.root.bind("<Configure>", self.on_resize)
        # 绑定截图快捷键
        self.root.bind_all('<F2>', lambda event: self.take_screenshot())
        self.root.bind_all('<Control-Shift-Z>', lambda event: self.take_screenshot())
        
        # 绑定回车键保存
        self.root.bind_all('<Return>', lambda event: self.on_enter_pressed())
        
        # 居中窗口
        self.center_window()
        
        # 设置窗口关闭协议
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_icons(self):
        """加载应用图标和按钮图标"""
        try:
            # 图标路径
            icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "icons")
            
            # 如果图标目录不存在，则创建
            if not os.path.exists(icons_dir):
                os.makedirs(icons_dir)
                print(f"创建图标目录: {icons_dir}")
            
            # 加载图标 (如果文件不存在，不会崩溃，只是不显示图标)
            self.icons = {}
            icon_files = {
                "app": "app_icon.ico",
                "screenshot": "screenshot.png",
                "save": "save.png",
                "clear": "clear.png",
                "query": "query.png",
            }
            
            for icon_name, file_name in icon_files.items():
                icon_path = os.path.join(icons_dir, file_name)
                try:
                    if os.path.exists(icon_path):
                        if icon_name == "app" and file_name.endswith(".ico"):
                            self.root.iconbitmap(icon_path)
                        else:
                            img = Image.open(icon_path)
                            img = img.resize((24, 24), Image.LANCZOS)
                            self.icons[icon_name] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"图标加载失败 {icon_name}: {e}")
        except Exception as e:
            print(f"图标加载过程出错: {e}")
    
    def _setup_styles(self):
        """
        设置UI样式
        """
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 现代风格
        
        # 配置基本样式
        self.style.configure(".", 
                           font=UI_FONT_NORMAL,
                           background=COLOR_BACKGROUND)
        
        # 标题标签
        self.style.configure("Title.TLabel", 
                           font=UI_FONT_TITLE,
                           foreground=COLOR_NEUTRAL,
                           background=COLOR_BACKGROUND,
                           padding=10)
        
        # 普通标签
        self.style.configure("TLabel", 
                           font=UI_FONT_NORMAL,
                           background=COLOR_BACKGROUND)
        
        # 小号标签
        self.style.configure("Small.TLabel", 
                           font=UI_FONT_SMALL,
                           foreground="#888",
                           background=COLOR_BACKGROUND)
        
        # 信息标签
        self.style.configure("Info.TLabel", 
                           foreground=COLOR_PRIMARY,
                           background=COLOR_BACKGROUND)
        
        # 主要按钮
        self.style.configure("Primary.TButton", 
                           font=UI_FONT_BOLD,
                           padding=8)
        
        self.style.map("Primary.TButton",
                     background=[('active', COLOR_PRIMARY), ('!disabled', COLOR_PRIMARY)],
                     foreground=[('active', 'white'), ('!disabled', 'white')])
        
        # 成功按钮
        self.style.configure("Success.TButton", 
                           font=UI_FONT_BOLD,
                           padding=8)
        
        self.style.map("Success.TButton",
                     background=[('active', COLOR_SUCCESS), ('!disabled', COLOR_SUCCESS)],
                     foreground=[('active', 'white'), ('!disabled', 'white')])
        
        # 警告按钮
        self.style.configure("Warning.TButton", 
                           font=UI_FONT_BOLD,
                           padding=8)
        
        self.style.map("Warning.TButton",
                     background=[('active', COLOR_WARNING), ('!disabled', COLOR_WARNING)],
                     foreground=[('active', 'white'), ('!disabled', 'white')])
        
        # 普通按钮
        self.style.configure("TButton", 
                           font=UI_FONT_NORMAL,
                           padding=8)
        
        # 标签框
        self.style.configure("TLabelframe", 
                           font=UI_FONT_BOLD,
                           background=COLOR_BACKGROUND)
        
        self.style.configure("TLabelframe.Label", 
                           font=UI_FONT_LARGE,
                           background=COLOR_BACKGROUND,
                           foreground=COLOR_NEUTRAL)
        
        # 分隔线
        self.style.configure("TSeparator", 
                           background="#ddd")
        
        # 单选按钮
        self.style.configure("TRadiobutton", 
                           font=UI_FONT_NORMAL,
                           background=COLOR_BACKGROUND)
        
        # 修改Entry样式
        self.style.map('TEntry', 
                     fieldbackground=[('disabled', '#f6f6f6')])
    
    def _create_widgets(self):
        """
        创建UI组件
        """
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部标题和信息
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 标题和时间放在同一行
        title_frame = ttk.Frame(self.header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(title_frame, text="工作记录系统", style="Title.TLabel").pack(side=tk.LEFT)
        
        # 时间显示放右侧
        self.time_frame = ttk.Frame(self.header_frame)
        self.time_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(self.time_frame, text="当前时间:", font=UI_FONT_BOLD).pack(side=tk.LEFT)
        self.time_label = ttk.Label(self.time_frame, text="", style="Info.TLabel")
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # 添加分隔线
        ttk.Separator(self.main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 15))
        
        # 创建分隔窗格 - 左侧控制区域，右侧预览区域
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制区域
        self.control_frame = ttk.Frame(self.paned_window, padding=15)
        self.paned_window.add(self.control_frame, weight=1)
        
        # 右侧预览区域
        self.preview_container = ttk.Frame(self.paned_window, padding=15)
        self.paned_window.add(self.preview_container, weight=2)
        
        # 在左侧控制区域创建组件
        self._create_task_frame()
        self._create_reminder_frame()  # 添加定时提醒区域
        self._create_button_frame()
        
        # 在右侧创建预览区域
        self._create_preview_frame()
        
        # 在主界面底部加快捷键提示
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))
        
        self.status_label = ttk.Label(footer_frame, text="就绪", style="Small.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        # 版权信息居中
        ttk.Label(
            footer_frame, 
            text="© 2023-2024 留痕软件", 
            style="Small.TLabel"
        ).pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # 快捷键提示
        self.hotkey_label = ttk.Label(
            footer_frame, 
            text="截图快捷键：F2 或 Ctrl+Shift+Z | 保存：Enter", 
            style="Small.TLabel"
        )
        self.hotkey_label.pack(side=tk.RIGHT)
    
    def _create_task_frame(self):
        """
        创建任务输入框架
        """
        # 任务信息区域
        task_group = ttk.LabelFrame(self.control_frame, text="任务信息", padding=15)
        task_group.pack(fill=tk.X, pady=(0, 15))
        
        # 项目/事务输入框
        task_frame = ttk.Frame(task_group)
        task_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(task_frame, text="项目/事务:", font=UI_FONT_BOLD).pack(side=tk.TOP, anchor='w', pady=(0, 5))
        self.task_entry = ttk.Entry(task_frame, font=UI_FONT_NORMAL)
        self.task_entry.pack(side=tk.TOP, fill=tk.X)
        
        # 添加备注输入区域
        notes_frame = ttk.Frame(task_group)
        notes_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(notes_frame, text="备注说明:", font=UI_FONT_BOLD).pack(side=tk.TOP, anchor='w', pady=(0, 5))
        self.notes_entry = ttk.Entry(notes_frame, font=UI_FONT_NORMAL)
        self.notes_entry.pack(side=tk.TOP, fill=tk.X)
    
    def _create_reminder_frame(self):
        """
        创建定时提醒区域
        """
        reminder_group = ttk.LabelFrame(self.control_frame, text="定时提醒", padding=15)
        reminder_group.pack(fill=tk.X, pady=(0, 15))
        
        # 创建定时提醒输入框
        reminder_frame = ttk.Frame(reminder_group)
        reminder_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(reminder_frame, text="提醒时间:", font=UI_FONT_BOLD).pack(side=tk.LEFT, anchor='w', pady=(0, 5))
        self.reminder_entry = ttk.Entry(reminder_frame, font=UI_FONT_NORMAL, width=10)
        self.reminder_entry.insert(0, DEFAULT_REMINDER_TIME)  # 设置默认提醒时间
        self.reminder_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # 添加提醒状态显示
        self.reminder_status_var = tk.StringVar(value="未设置")
        self.reminder_status = ttk.Label(reminder_frame, textvariable=self.reminder_status_var, style="Info.TLabel")
        self.reminder_status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 添加按钮区域
        btn_frame = ttk.Frame(reminder_group)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 添加启用/禁用提醒按钮
        self.reminder_btn = ttk.Button(
            btn_frame, 
            text="启用提醒",
            style="Primary.TButton",
            command=self.toggle_reminder
        )
        self.reminder_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # 添加立即提醒按钮
        self.remind_now_btn = ttk.Button(
            btn_frame, 
            text="立即提醒",
            command=self.show_reminder_now
        )
        self.remind_now_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 添加分隔线
        ttk.Separator(reminder_group, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 创建间隔提醒区域
        interval_frame = ttk.Frame(reminder_group)
        interval_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 添加间隔提醒标签
        ttk.Label(interval_frame, text=f"每 {INTERVAL_REMINDER_MINUTES} 分钟提醒一次", font=UI_FONT_BOLD).pack(side=tk.LEFT, anchor='w', pady=(0, 5))
        
        # 间隔提醒状态
        self.interval_status_var = tk.StringVar(value="未启用")
        self.interval_status = ttk.Label(interval_frame, textvariable=self.interval_status_var, style="Info.TLabel")
        self.interval_status.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 间隔提醒按钮区域
        interval_btn_frame = ttk.Frame(reminder_group)
        interval_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 启用/禁用间隔提醒按钮
        self.interval_btn = ttk.Button(
            interval_btn_frame, 
            text="启用间隔提醒",
            style="Warning.TButton",
            command=self.toggle_interval_reminder
        )
        self.interval_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # 重置间隔提醒按钮
        self.reset_interval_btn = ttk.Button(
            interval_btn_frame, 
            text="重置计时器",
            command=self.reset_interval_reminder,
            state=tk.DISABLED
        )
        self.reset_interval_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_preview_frame(self):
        """
        创建预览框架
        """
        self.preview_frame = ttk.LabelFrame(self.preview_container, text="截图预览", padding=15)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 预览背景
        preview_bg = ttk.Frame(self.preview_frame, padding=10)
        preview_bg.pack(fill=tk.BOTH, expand=True)
        
        # 图片预览标签
        self.preview_label = ttk.Label(
            preview_bg, 
            borderwidth=1, 
            relief="solid", 
            anchor="center", 
            background=COLOR_PREVIEW_BG
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 添加空白预览提示
        self.empty_preview_text = tk.StringVar(value="等待截图...\n按下 F2 或 Ctrl+Shift+Z 快捷键，或点击'截图'按钮")
        self.preview_label.config(text=self.empty_preview_text.get(), foreground="#888")
    
    def _create_button_frame(self):
        """
        创建按钮框架
        """
        # 截图配置区域
        screenshot_group = ttk.LabelFrame(self.control_frame, text="截图配置", padding=15)
        screenshot_group.pack(fill=tk.X, pady=(0, 15))
        
        # 创建截图类型选择
        ttk.Label(screenshot_group, text="截图类型:", font=UI_FONT_BOLD).pack(side=tk.TOP, anchor='w', pady=(0, 5))
        
        # 创建单选按钮变量和选项
        self.screenshot_type = tk.StringVar(value="full")
        
        radio_frame = ttk.Frame(screenshot_group)
        radio_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(
            radio_frame, 
            text="全屏截图", 
            variable=self.screenshot_type, 
            value="full"
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            radio_frame, 
            text="区域截图", 
            variable=self.screenshot_type, 
            value="region"
        ).pack(side=tk.LEFT)
        
        # 操作按钮区域
        button_group = ttk.LabelFrame(self.control_frame, text="操作", padding=15)
        button_group.pack(fill=tk.X)
        
        # 主要操作按钮
        main_buttons = ttk.Frame(button_group)
        main_buttons.pack(fill=tk.X, pady=(0, 10))
        
        # 截图按钮
        self.screenshot_btn = ttk.Button(
            main_buttons, 
            text="截图",
            style="Primary.TButton",
            command=self.take_screenshot
        )
        
        # 如果加载了图标，设置图标
        if hasattr(self, 'icons') and 'screenshot' in self.icons:
            self.screenshot_btn.config(image=self.icons['screenshot'], compound=tk.LEFT)
            
        self.screenshot_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # 保存按钮
        self.save_btn = ttk.Button(
            main_buttons, 
            text="保存",
            style="Success.TButton",
            command=self.save_screenshot
        )
        
        if hasattr(self, 'icons') and 'save' in self.icons:
            self.save_btn.config(image=self.icons['save'], compound=tk.LEFT)
            
        self.save_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.save_btn.config(state="disabled")  # 初始状态禁用
        
        # 次要按钮
        secondary_buttons = ttk.Frame(button_group)
        secondary_buttons.pack(fill=tk.X)
        
        # 清除按钮
        self.clear_btn = ttk.Button(
            secondary_buttons, 
            text="清除",
            command=self.clear_screenshot
        )
        
        if hasattr(self, 'icons') and 'clear' in self.icons:
            self.clear_btn.config(image=self.icons['clear'], compound=tk.LEFT)
            
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        self.clear_btn.config(state="disabled")  # 初始状态禁用
        
        # 添加查询记录按钮
        self.query_btn = ttk.Button(
            secondary_buttons, 
            text="查询记录",
            command=self.open_records_view
        )
        
        if hasattr(self, 'icons') and 'query' in self.icons:
            self.query_btn.config(image=self.icons['query'], compound=tk.LEFT)
            
        self.query_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def update_time(self):
        """
        更新时间显示
        """
        self.time_label.config(text=get_current_time_str())
        self.root.after(1000, self.update_time)  # 每秒更新一次
    
    def on_enter_pressed(self):
        """
        当按下回车键时，如果有截图则保存，否则进行截图
        """
        if self.current_screenshot and self.save_btn['state'] != 'disabled':
            self.save_screenshot()
        else:
            self.take_screenshot()
    
    def take_screenshot(self):
        """
        捕获屏幕截图
        """
        self.status_label.config(text="正在截图...")
        
        # 根据选择的截图类型执行不同的截图功能
        screenshot_type = self.screenshot_type.get()
        
        try:
            if screenshot_type == "full":
                # 全屏截图
                self.current_screenshot = take_fullscreen_screenshot(self.root)
            else:
                # 区域截图
                self.current_screenshot = take_region_screenshot(self.root)
            
            # 如果截图成功
            if self.current_screenshot:
                # 打开编辑器让用户进行标注
                editor = ScreenshotEditor(self.root, self.current_screenshot)
                edited_image = editor.get_result()
                
                if edited_image:  # 如果用户完成了编辑
                    self.current_screenshot = edited_image
                    # 调整图像大小以适应预览区域
                    self.display_screenshot()
                    
                    # 启用保存和清除按钮
                    self.save_btn.config(state="normal")
                    self.clear_btn.config(state="normal")
                    
                    # 更新状态
                    self.status_label.config(text="截图完成，等待保存")
                else:  # 用户取消了编辑
                    self.current_screenshot = None
                    self.screenshot_preview = None
                    self.preview_label.config(image="", text=self.empty_preview_text.get())
                    self.status_label.config(text="截图已取消")
                    messagebox.showinfo("提示", "截图已取消")
            else:
                # 截图失败或用户取消
                self.status_label.config(text="截图已取消")
                messagebox.showinfo("提示", "截图已取消")
                
                # 清空当前截图
                self.current_screenshot = None
                self.screenshot_preview = None
                self.preview_label.config(image="", text=self.empty_preview_text.get())
        except Exception as e:
            self.status_label.config(text="截图失败")
            messagebox.showerror("错误", f"截图过程中发生错误: {str(e)}")
            print(f"截图错误: {e}")
    
    def display_screenshot(self):
        """
        在预览区域显示截图
        """
        if self.current_screenshot:
            # 获取预览区域的大小
            preview_width = self.preview_frame.winfo_width() - 40  # 减去padding
            preview_height = self.preview_frame.winfo_height() - 40
            
            # 如果窗口还没有完全初始化，使用默认大小
            if preview_width <= 1 or preview_height <= 1:
                preview_width = 600
                preview_height = 400
            
            # 调整图像并显示
            self.screenshot_preview = resize_image_for_preview(
                self.current_screenshot, preview_width, preview_height)
            
            # 更新预览标签
            self.preview_label.config(image=self.screenshot_preview, text="")
    
    def save_screenshot(self):
        """
        保存截图
        """
        task = self.task_entry.get().strip()
        notes = self.notes_entry.get().strip()
        
        # 检查任务名称是否为空
        if not task:
            messagebox.showwarning("警告", "请输入项目/事务名称后再保存")
            self.task_entry.focus_set()
            return
            
        self.status_label.config(text="正在保存...")
        
        try:
            success, result = save_screenshot(self.current_screenshot, task, notes)
            
            if success:
                self.status_label.config(text=f"已保存: {os.path.basename(result)}")
                messagebox.showinfo("成功", f"截图已保存为：{os.path.basename(result)}")
                # 清空当前内容，准备下一次截图
                self.clear_screenshot()
            else:
                self.status_label.config(text="保存失败")
                messagebox.showerror("错误", result)
        except Exception as e:
            self.status_label.config(text="保存失败")
            messagebox.showerror("错误", f"保存过程中发生错误: {str(e)}")
            print(f"保存错误: {e}")
    
    def clear_screenshot(self):
        """
        清除当前截图
        """
        self.current_screenshot = None
        self.screenshot_preview = None
        self.preview_label.config(image="", text=self.empty_preview_text.get())
        self.notes_entry.delete(0, tk.END)  # 清空备注内容
        self.save_btn.config(state="disabled")
        self.clear_btn.config(state="disabled")
        self.status_label.config(text="就绪")
    
    def open_records_view(self):
        """
        打开记录查询界面
        """
        self.status_label.config(text="打开记录查询...")
        RecordsView(self.root)
        self.status_label.config(text="就绪")

    def on_resize(self, event):
        """
        窗口大小改变时调整预览图像
        
        Args:
            event: 窗口大小改变事件
        """
        if self.current_screenshot:
            self.display_screenshot()
    
    def on_closing(self):
        """
        窗口关闭时的处理
        """
        # 停止提醒线程
        if self.reminder_active:
            self.stop_reminder()
        
        # 停止间隔提醒线程
        if self.interval_reminder_active:
            self.stop_interval_reminder()
        
        # 关闭窗口
        self.root.destroy()

    def toggle_reminder(self):
        """
        启用或禁用定时提醒
        """
        if self.reminder_active:
            # 禁用提醒
            self.stop_reminder()
            self.reminder_btn.config(text="启用提醒")
            self.reminder_status_var.set("未设置")
            self.status_label.config(text="定时提醒已关闭")
        else:
            # 启用提醒
            time_str = self.reminder_entry.get().strip()
            result = parse_time_string(time_str)
            
            if not result:
                messagebox.showerror("错误", "请输入有效的时间格式，如 17:30")
                return
            
            hours, minutes = result
            self.start_reminder(hours, minutes)
    
    def start_reminder(self, hours, minutes):
        """
        启动定时提醒
        
        Args:
            hours: 小时 (0-23)
            minutes: 分钟 (0-59)
        """
        # 停止任何现有的提醒
        self.stop_reminder()
        
        # 计算下一次提醒的时间
        self.next_reminder_time = calculate_next_reminder_time(hours, minutes)
        
        # 更新状态
        self.reminder_active = True
        self.reminder_btn.config(text="禁用提醒")
        
        # 创建并启动提醒线程
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()
        
        # 显示下一次提醒的时间
        self.update_reminder_status()
        self.status_label.config(text=f"定时提醒已设置：{hours:02d}:{minutes:02d}")
        
    def stop_reminder(self):
        """
        停止定时提醒
        """
        self.reminder_active = False
        self.next_reminder_time = None
        self.reminder_thread = None  # 线程会自动结束，因为它是守护线程
    
    def update_reminder_status(self):
        """
        更新提醒状态显示
        """
        if not self.reminder_active or not self.next_reminder_time:
            self.reminder_status_var.set("未设置")
            return
        
        seconds_left = time_until_next_reminder(self.next_reminder_time)
        time_left_str = format_time_delta(seconds_left)
        next_time_str = self.next_reminder_time.strftime("%H:%M")
        
        self.reminder_status_var.set(f"下次提醒: {next_time_str} (剩余 {time_left_str})")
        
        # 每分钟更新一次
        self.root.after(60000, self.update_reminder_status)
    
    def _reminder_loop(self):
        """
        提醒线程的主循环
        """
        while self.reminder_active and self.next_reminder_time:
            # 计算等待时间
            seconds_to_wait = time_until_next_reminder(self.next_reminder_time)
            
            if seconds_to_wait <= 0:
                # 到达提醒时间，触发提醒
                self._trigger_reminder()
                
                # 更新为下一天的同一时间
                hours = self.next_reminder_time.hour
                minutes = self.next_reminder_time.minute
                self.next_reminder_time = calculate_next_reminder_time(hours, minutes)
                
                # 更新状态
                self.root.after(0, self.update_reminder_status)
            
            # 等待1分钟或剩余时间（较小值）
            time.sleep(min(60, max(1, seconds_to_wait)))
            
            # 如果提醒已被禁用，退出循环
            if not self.reminder_active:
                break
    
    def _trigger_reminder(self):
        """
        触发提醒操作
        """
        # 使用after方法在主线程中执行UI操作
        self.root.after(0, self.show_reminder)
    
    def show_reminder(self):
        """
        显示提醒对话框
        """
        # 弹出提醒窗口
        messagebox.showinfo("工作记录提醒", REMINDER_MESSAGE)
        
        # 播放提醒声音
        if REMINDER_SOUND_ENABLED:
            self.root.bell()  # 使用系统默认声音
    
    def show_reminder_now(self):
        """
        立即显示提醒（用于测试）
        """
        self.show_reminder()
        self.status_label.config(text="已显示提醒")

    def toggle_interval_reminder(self):
        """
        启用或禁用间隔提醒
        """
        if self.interval_reminder_active:
            # 禁用间隔提醒
            self.stop_interval_reminder()
            self.interval_btn.config(text="启用间隔提醒")
            self.interval_status_var.set("未启用")
            self.status_label.config(text="间隔提醒已关闭")
        else:
            # 启用间隔提醒
            self.start_interval_reminder()
    
    def start_interval_reminder(self):
        """
        启动间隔提醒
        """
        # 停止任何现有的间隔提醒
        self.stop_interval_reminder()
        
        # 计算下一次间隔提醒的时间
        self.next_interval_time = calculate_next_interval_reminder()
        
        # 更新状态
        self.interval_reminder_active = True
        self.interval_btn.config(text="禁用间隔提醒")
        self.reset_interval_btn.config(state=tk.NORMAL)  # 启用重置按钮
        
        # 创建并启动间隔提醒线程
        self.interval_reminder_thread = threading.Thread(target=self._interval_loop, daemon=True)
        self.interval_reminder_thread.start()
        
        # 显示下一次间隔提醒的时间
        self.update_interval_status()
        self.status_label.config(text=f"间隔提醒已设置：{self.next_interval_time.strftime('%H:%M')}")
        
    def stop_interval_reminder(self):
        """
        停止间隔提醒
        """
        self.interval_reminder_active = False
        self.next_interval_time = None
        self.interval_reminder_thread = None  # 线程会自动结束，因为它是守护线程
        self.reset_interval_btn.config(state=tk.DISABLED)  # 禁用重置按钮
    
    def update_interval_status(self):
        """
        更新间隔提醒状态显示
        """
        if not self.interval_reminder_active or not self.next_interval_time:
            self.interval_status_var.set("未启用")
            return
        
        seconds_left = time_until_next_reminder(self.next_interval_time)
        time_left_str = format_time_delta(seconds_left)
        next_time_str = self.next_interval_time.strftime("%H:%M")
        
        self.interval_status_var.set(f"下次提醒: {next_time_str} (剩余 {time_left_str})")
        
        # 每分钟更新一次
        self.root.after(60000, self.update_interval_status)
    
    def _interval_loop(self):
        """
        间隔提醒线程的主循环
        """
        while self.interval_reminder_active and self.next_interval_time:
            # 计算等待时间
            seconds_to_wait = time_until_next_reminder(self.next_interval_time)
            
            if seconds_to_wait <= 0:
                # 到达间隔提醒时间，触发提醒
                self._trigger_interval_reminder()
                
                # 计算下一次间隔提醒时间
                self.next_interval_time = calculate_next_interval_reminder()
                
                # 更新状态
                self.root.after(0, self.update_interval_status)
            
            # 等待1分钟或剩余时间（较小值）
            time.sleep(min(60, max(1, seconds_to_wait)))
            
            # 如果提醒已被禁用，退出循环
            if not self.interval_reminder_active:
                break
    
    def _trigger_interval_reminder(self):
        """
        触发间隔提醒操作
        """
        # 使用after方法在主线程中执行UI操作
        self.root.after(0, self.show_interval_reminder)
    
    def show_interval_reminder(self):
        """
        显示间隔提醒对话框
        """
        # 弹出间隔提醒窗口
        messagebox.showinfo("工作间隔提醒", INTERVAL_REMINDER_MESSAGE)
        
        # 播放间隔提醒声音
        if REMINDER_SOUND_ENABLED:
            self.root.bell()  # 使用系统默认声音
    
    def reset_interval_reminder(self):
        """
        重置间隔提醒
        """
        if not self.interval_reminder_active:
            return
            
        # 重新计算下一次间隔提醒的时间
        self.next_interval_time = calculate_next_interval_reminder()
        
        # 更新状态显示
        self.update_interval_status()
        self.status_label.config(text="间隔提醒已重置，计时器已重新开始")