import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import math

from src.config import (
    COLOR_BACKGROUND, COLOR_NEUTRAL, COLOR_PRIMARY,
    DARK_COLOR_BACKGROUND, DARK_COLOR_NEUTRAL, DARK_COLOR_PRIMARY,
    UI_FONT_BOLD, UI_FONT_NORMAL, UI_FONT_TITLE, UI_FONT_LARGE, UI_FONT_SMALL
)

class ScreenshotEditor(tk.Toplevel):
    def __init__(self, parent, image, is_dark_mode=False):
        super().__init__(parent)
        self.title("截图编辑器 - 标注并保存")
        
        # 主题设置
        self.is_dark_mode = is_dark_mode
        if hasattr(parent, 'is_dark_mode'):
            self.is_dark_mode = parent.is_dark_mode
            
        self.theme_colors = self.get_theme_colors()
        
        self.configure(bg=self.theme_colors["background"])  # 设置窗口背景色
        
        # 动态获取屏幕分辨率和按钮区宽高
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        button_area_width = 220  # 右侧按钮区宽度增加
        button_area_height = 150 # 顶部/底部控件高度
        max_width = min(1600, int(screen_w * 0.9)) - button_area_width
        max_height = min(900, int(screen_h * 0.9)) - button_area_height
        img_width, img_height = image.size
        if img_width > max_width or img_height > max_height:
            ratio = min(max_width/img_width, max_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)
        # 设置窗口大小时加上按钮区
        self.geometry(f"{image.width + 100}x{image.height + 160}")
        self.resizable(True, True)
        self.image = image.copy()
        self.original_image = image.copy()  # 保存原始图片用于清除
        self.draw = ImageDraw.Draw(self.image)
        self.rect_start = None
        self.rect_id = None
        self.rects = []  # 已画矩形列表，每个元素为 (type, coords, color, text)
        self.current_color = '#FF4136'  # 更美观的默认红色
        self.current_tool = 'rect'  # 当前工具：rect, arrow, text, mosaic
        self.current_text = ""  # 当前文字
        self.font_size = 20  # 默认字体大小
        self.mosaic_size = 40  # 马赛克块大小，默认40
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.zoom_scale = 1.0  # 当前缩放比例
        self.min_zoom = 0.2
        self.max_zoom = 3.0
        self._last_wheel_mouse = (0, 0)  # 记录滚轮缩放时鼠标位置
        
        # 创建自定义样式
        self.create_styles()
        
        # 创建左侧工具区（竖直工具栏）
        tools_panel = tk.Frame(self, bg=self.theme_colors["panel_bg"], bd=0, highlightthickness=1, highlightbackground=self.theme_colors["border"])
        tools_panel.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        # 添加标题和版本信息
        title_frame = tk.Frame(tools_panel, bg=self.theme_colors["panel_bg"], height=50)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(title_frame, text="截图编辑器", font=UI_FONT_TITLE, foreground=self.theme_colors["text"], background=self.theme_colors["panel_bg"]).pack(side=tk.TOP, pady=(12, 0))
        ttk.Label(title_frame, text="v1.0", font=UI_FONT_SMALL, foreground=self.theme_colors["secondary_text"], background=self.theme_colors["panel_bg"]).pack(side=tk.TOP, pady=(0, 10))
        
        # 添加工具标签
        ttk.Label(tools_panel, text="编辑工具", font=("微软雅黑", 11, "bold"), style="Section.TLabel").pack(side=tk.TOP, pady=(5, 8), padx=12, anchor='w')
        
        # 工具按钮容器
        tools_frame = tk.Frame(tools_panel, bg=self.theme_colors["panel_bg"], padx=5)
        tools_frame.pack(side=tk.TOP, fill=tk.X, padx=5)
        
        self.tool_var = tk.StringVar(value='rect')
        self.tool_btns = {}
        
        # 工具图标和名称（可以替换为实际图标）
        tool_info = [
            ('rect', '矩形', '◻'),
            ('arrow', '箭头', '↗'),
            ('text', '文字', 'T'),
            ('mosaic', '马赛克', '▦')
        ]
        
        # 创建工具按钮网格布局
        for i, (tool, text, icon) in enumerate(tool_info):
            row, col = i // 2, i % 2
            btn_frame = tk.Frame(tools_frame, bg=self.theme_colors["panel_bg"])
            btn_frame.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            
            btn = ttk.Radiobutton(
                btn_frame, 
                text=f"{icon} {text}", 
                compound=tk.LEFT,
                variable=self.tool_var, 
                value=tool, 
                command=self.on_tool_change, 
                style="ToolButton.TRadiobutton"
            )
            btn.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
            self.tool_btns[tool] = btn
        
        # 均分列宽
        tools_frame.grid_columnconfigure(0, weight=1)
        tools_frame.grid_columnconfigure(1, weight=1)
        
        # 分隔线
        ttk.Separator(tools_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=12, padx=10)
        
        # 样式设置区域
        ttk.Label(tools_panel, text="样式设置", font=("微软雅黑", 11, "bold"), style="Section.TLabel").pack(side=tk.TOP, pady=(0, 8), padx=12, anchor='w')
        
        # 色彩区域
        color_frame = tk.Frame(tools_panel, bg=self.theme_colors["panel_bg"])
        color_frame.pack(side=tk.TOP, fill=tk.X, padx=12, pady=4)
        
        # 预设颜色选择
        ttk.Label(color_frame, text="颜色：", font=("微软雅黑", 10), style="Option.TLabel").grid(row=0, column=0, sticky='w', pady=2)
        colors_frame = tk.Frame(color_frame, bg=self.theme_colors["panel_bg"])
        colors_frame.grid(row=0, column=1, sticky='w')
        
        # 常用颜色预设 - 增加更多高对比度颜色
        preset_colors = [
            '#FF4136',  # 亮红色
            '#0074D9',  # 亮蓝色
            '#2ECC40',  # 亮绿色
            '#FFDC00',  # 亮黄色
            '#FF851B',  # 橙色
            '#F012BE',  # 亮粉色
            '#B10DC9',  # 紫色
            '#FFFFFF',  # 白色
        ]
        
        # 第二行颜色
        row1_colors = preset_colors[:4]  # 第一行4种颜色
        row2_colors = preset_colors[4:]  # 第二行4种颜色
        
        # 创建第一行颜色按钮
        for i, color in enumerate(row1_colors):
            color_btn = tk.Canvas(colors_frame, width=16, height=16, bg=color, cursor="hand2", highlightthickness=1, highlightbackground=self.theme_colors["border"])
            color_btn.grid(row=0, column=i, padx=2)
            color_btn.bind('<Button-1>', lambda e, c=color: self.select_preset_color(c))
        
        # 创建第二行颜色按钮
        for i, color in enumerate(row2_colors):
            color_btn = tk.Canvas(colors_frame, width=16, height=16, bg=color, cursor="hand2", highlightthickness=1, highlightbackground=self.theme_colors["border"])
            color_btn.grid(row=1, column=i, padx=2, pady=2)
            color_btn.bind('<Button-1>', lambda e, c=color: self.select_preset_color(c))
        
        # 自定义颜色按钮
        self.color_btn = ttk.Button(color_frame, text="自定义...", command=self.choose_color, style="Small.TButton", width=8)
        self.color_btn.grid(row=0, column=len(row1_colors)+1, rowspan=2, padx=(5, 0))
        
        # 当前颜色预览
        preview_frame = tk.Frame(color_frame, bg=self.theme_colors["panel_bg"])
        preview_frame.grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 0))
        ttk.Label(preview_frame, text="当前：", font=("微软雅黑", 10), style="Option.TLabel").pack(side=tk.LEFT)
        self.color_preview = tk.Canvas(preview_frame, width=24, height=24, bg=self.current_color, highlightthickness=1, highlightbackground=self.theme_colors["border"])
        self.color_preview.pack(side=tk.LEFT, padx=5)
        
        # 字体大小选择（文字工具）
        self.font_size_frame = tk.Frame(tools_panel, bg=self.theme_colors["panel_bg"])
        ttk.Label(self.font_size_frame, text="字体大小：", font=("微软雅黑", 10), style="Option.TLabel").pack(side=tk.TOP, anchor='w')
        font_size_control = tk.Frame(self.font_size_frame, bg=self.theme_colors["panel_bg"])
        font_size_control.pack(side=tk.TOP, fill=tk.X, pady=(4, 0))
        
        # 字体大小调整按钮
        decrease_btn = ttk.Button(font_size_control, text="-", width=2, command=lambda: self.adjust_font_size(-2), style="Round.TButton")
        decrease_btn.pack(side=tk.LEFT)
        
        self.font_size_var = tk.StringVar(value=str(self.font_size))
        self.font_size_entry = ttk.Entry(font_size_control, textvariable=self.font_size_var, width=3, justify='center')
        self.font_size_entry.pack(side=tk.LEFT, padx=4)
        self.font_size_entry.bind('<Return>', self.on_font_size_change)
        
        increase_btn = ttk.Button(font_size_control, text="+", width=2, command=lambda: self.adjust_font_size(2), style="Round.TButton")
        increase_btn.pack(side=tk.LEFT)
        
        # 字体样式预览
        self.font_preview = ttk.Label(self.font_size_frame, text="文字预览", font=("微软雅黑", self.font_size), foreground=self.current_color, background=self.theme_colors["panel_bg"])
        self.font_preview.pack(side=tk.TOP, pady=(8, 0), anchor='w')
        
        self.font_size_frame.pack_forget()  # 初始隐藏
        
        # 马赛克大小选择
        self.mosaic_size_frame = tk.Frame(tools_panel, bg=self.theme_colors["panel_bg"])
        ttk.Label(self.mosaic_size_frame, text="马赛克大小：", font=("微软雅黑", 10), style="Option.TLabel").pack(side=tk.TOP, anchor='w')
        
        mosaic_value_frame = tk.Frame(self.mosaic_size_frame, bg=self.theme_colors["panel_bg"])
        mosaic_value_frame.pack(side=tk.TOP, fill=tk.X, pady=(4, 0))
        
        self.mosaic_size_var = tk.IntVar(value=self.mosaic_size)
        self.mosaic_size_spin = ttk.Spinbox(
            mosaic_value_frame, 
            from_=5, 
            to=100, 
            increment=5, 
            textvariable=self.mosaic_size_var, 
            width=5, 
            command=self.on_mosaic_size_spin
        )
        self.mosaic_size_spin.pack(side=tk.LEFT)
        
        ttk.Label(mosaic_value_frame, text="px", style="Option.TLabel").pack(side=tk.LEFT, padx=(2, 0))
        
        # 带标签的滑块
        scale_frame = tk.Frame(self.mosaic_size_frame, bg=self.theme_colors["panel_bg"])
        scale_frame.pack(side=tk.TOP, fill=tk.X, pady=(8, 0))
        
        ttk.Label(scale_frame, text="小", style="Scale.TLabel").pack(side=tk.LEFT)
        self.mosaic_size_scale = ttk.Scale(
            scale_frame, 
            from_=5, 
            to=100, 
            orient=tk.HORIZONTAL, 
            variable=self.mosaic_size_var, 
            command=self.on_mosaic_size_scale, 
            length=120
        )
        self.mosaic_size_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Label(scale_frame, text="大", style="Scale.TLabel").pack(side=tk.LEFT)
        
        self.mosaic_size_frame.pack_forget()  # 初始隐藏
        
        # 分隔线
        ttk.Separator(tools_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=12, padx=10)
        
        # 操作区域
        ttk.Label(tools_panel, text="操作", font=("微软雅黑", 11, "bold"), style="Section.TLabel").pack(side=tk.TOP, pady=(0, 8), padx=12, anchor='w')
        
        # 按钮容器
        buttons_frame = tk.Frame(tools_panel, bg=self.theme_colors["panel_bg"], padx=12)
        buttons_frame.pack(side=tk.TOP, fill=tk.X)
        
        # 撤销和清除按钮，放在一行
        actions_frame = tk.Frame(buttons_frame, bg=self.theme_colors["panel_bg"])
        actions_frame.pack(side=tk.TOP, fill=tk.X, pady=4)
        
        self.undo_btn = ttk.Button(
            actions_frame, 
            text="撤销上一步", 
            command=self.undo_last, 
            width=10,
            style="Action.TButton"
        )
        self.undo_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self.undo_btn.config(state="disabled")
        
        self.clear_btn = ttk.Button(
            actions_frame, 
            text="清除所有", 
            command=self.clear_all, 
            width=10,
            style="Action.TButton"
        )
        self.clear_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        self.clear_btn.config(state="disabled")
        
        # 保存按钮居中
        self.save_btn = ttk.Button(
            buttons_frame, 
            text="保存图片", 
            command=self.save_image,
            style="Primary.TButton"
        )
        self.save_btn.pack(side=tk.TOP, fill=tk.X, pady=(8, 0))
        
        # 底部信息
        bottom_frame = tk.Frame(tools_panel, bg=self.theme_colors["panel_bg"])
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        ttk.Label(
            bottom_frame, 
            text="滚轮可缩放图片\n按Esc取消文本输入", 
            justify=tk.CENTER,
            font=("微软雅黑", 8),
            foreground=self.theme_colors["secondary_text"],
            background=self.theme_colors["panel_bg"]
        ).pack(side=tk.BOTTOM, fill=tk.X)

        # 创建顶部工具栏（只放退出和完成按钮）
        toolbar = ttk.Frame(self, style="Toolbar.TFrame")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # 左侧标题
        ttk.Label(toolbar, text="图片编辑", font=("微软雅黑", 12, "bold"), style="Toolbar.TLabel").pack(side=tk.LEFT, padx=15, pady=12)
        
        # 右侧按钮
        right_btn_frame = ttk.Frame(toolbar, style="Toolbar.TFrame")
        right_btn_frame.pack(side=tk.RIGHT, padx=15, pady=8)
        
        self.ok_btn = ttk.Button(right_btn_frame, text="完成并返回", command=self.finish, style="Success.TButton")
        self.ok_btn.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_btn = ttk.Button(right_btn_frame, text="取消", command=self.cancel, style="Cancel.TButton")
        self.cancel_btn.pack(side=tk.RIGHT)

        # 创建主内容区（只放图片Canvas）
        main_frame = ttk.Frame(self, style="Canvas.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # 内容区背景使用主题色
        self.canvas = tk.Canvas(main_frame, width=image.width, height=image.height, bg=self.theme_colors["canvas_bg"], cursor="cross", bd=0, highlightthickness=1, highlightbackground=self.theme_colors["border"])
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas_img = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        
        # 状态
        self.result_image = None
        self.cancelled = False
        self.temp_text = None  # 临时文字对象
        self.text_entry = None  # 文字输入框
        self.mosaic_cursor_id = None  # 马赛克提示圈ID
        
        # 绑定事件
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_move)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_motion)
        self.canvas.bind('<Leave>', self.on_mouse_leave)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)  # Windows
        self.canvas.bind('<Button-4>', self.on_mouse_wheel)    # Linux
        self.canvas.bind('<Button-5>', self.on_mouse_wheel)    # Linux
        self.canvas.bind('<Enter>', self.on_mouse_enter)
        
        # 鼠标悬浮工具提示
        self.create_tooltips()
        
        # 设置窗口位置居中
        self.center_window()
        
        # 设置窗口图标(如果有)
        # self.iconbitmap("path/to/icon.ico")
    
    def get_theme_colors(self):
        """获取当前主题颜色"""
        if self.is_dark_mode:
            return {
                "background": DARK_COLOR_BACKGROUND,
                "panel_bg": "#252540",  # 稍微亮一点的深色
                "text": DARK_COLOR_NEUTRAL,
                "secondary_text": "#aaaaaa",
                "border": "#666666",  # 增强边框对比度
                "canvas_bg": "#2a2a42",
                "primary": DARK_COLOR_PRIMARY,
                "button_bg": "#333350",
                "button_active": "#444470",
                "preview_bg": "#2d2d44"
            }
        else:
            return {
                "background": COLOR_BACKGROUND,
                "panel_bg": "#f5f5f7",
                "text": COLOR_NEUTRAL,
                "secondary_text": "#888888",
                "border": "#999999",  # 增强边框对比度
                "canvas_bg": "#f9f9f9",
                "primary": COLOR_PRIMARY,
                "button_bg": "#f0f0f0",
                "button_active": "#e0e0e0",
                "preview_bg": "#f9f9f9"
            }
    
    def create_styles(self):
        """创建自定义样式"""
        style = ttk.Style()
        
        # 定义颜色
        primary_color = self.theme_colors["primary"]
        success_color = "#2ecc71" if not self.is_dark_mode else "#2ecc71"
        danger_color = "#e74c3c" if not self.is_dark_mode else "#e74c3c"
        warning_color = "#f39c12" if not self.is_dark_mode else "#f39c12"
        
        # 修改默认字体
        default_font = UI_FONT_NORMAL
        style.configure(".", font=default_font)
        
        # 节标题样式
        style.configure("Section.TLabel", 
                      font=("微软雅黑", 11, "bold"),
                      foreground=self.theme_colors["text"],
                      background=self.theme_colors["panel_bg"],
                      padding=4)
        
        # 选项标签样式
        style.configure("Option.TLabel", 
                      font=("微软雅黑", 10),
                      foreground=self.theme_colors["text"],
                      background=self.theme_colors["panel_bg"])
        
        # 比例尺标签
        style.configure("Scale.TLabel", 
                      font=("微软雅黑", 8),
                      foreground=self.theme_colors["secondary_text"],
                      background=self.theme_colors["panel_bg"])
        
        # 工具栏样式
        style.configure("Toolbar.TFrame", background=self.theme_colors["background"])
        style.configure("Toolbar.TLabel", 
                      background=self.theme_colors["background"],
                      foreground=self.theme_colors["text"])
        
        # 画布容器样式
        style.configure("Canvas.TFrame", 
                      background=self.theme_colors["background"],
                      relief="flat")
        
        # 工具按钮样式
        style.configure("ToolButton.TRadiobutton",
                      font=("微软雅黑", 10),
                      background=self.theme_colors["panel_bg"],
                      foreground=self.theme_colors["text"],
                      padding=10)
        
        active_bg = "#e8f0fe" if not self.is_dark_mode else "#444470"
        active_fg = "#0078d7" if not self.is_dark_mode else "#ffffff"
        
        style.map("ToolButton.TRadiobutton",
                background=[('selected', active_bg), ('active', active_bg)],
                foreground=[('selected', active_fg), ('active', active_fg)])
        
        # 主要动作按钮
        style.configure("Primary.TButton", 
                      font=("微软雅黑", 10, "bold"),
                      background=primary_color,
                      foreground="white")
        
        style.map("Primary.TButton",
                background=[('active', primary_color)])
        
        # 成功动作按钮
        style.configure("Success.TButton", 
                      font=("微软雅黑", 10, "bold"),
                      background=success_color,
                      foreground="white")
        
        style.map("Success.TButton",
                background=[('active', success_color)])
        
        # 取消按钮
        cancel_bg = "#f5f5f5" if not self.is_dark_mode else "#333350"
        cancel_active = "#e0e0e0" if not self.is_dark_mode else "#444470"
        
        style.configure("Cancel.TButton", 
                      font=("微软雅黑", 10),
                      background=cancel_bg,
                      foreground=self.theme_colors["text"])
        
        style.map("Cancel.TButton",
                background=[('active', cancel_active)])
        
        # 操作按钮
        style.configure("Action.TButton", 
                      font=("微软雅黑", 10),
                      padding=6,
                      background=self.theme_colors["button_bg"],
                      foreground=self.theme_colors["text"])
        
        style.map("Action.TButton",
                background=[('active', self.theme_colors["button_active"])])
        
        # 小按钮
        style.configure("Small.TButton", 
                      font=("微软雅黑", 9),
                      padding=3,
                      background=self.theme_colors["button_bg"],
                      foreground=self.theme_colors["text"])
        
        style.map("Small.TButton",
                background=[('active', self.theme_colors["button_active"])])
        
        # 圆形按钮
        style.configure("Round.TButton", 
                      font=("微软雅黑", 9, "bold"),
                      padding=0,
                      background=self.theme_colors["button_bg"],
                      foreground=self.theme_colors["text"])
        
        style.map("Round.TButton",
                background=[('active', self.theme_colors["button_active"])])
    
    def create_tooltips(self):
        """为按钮和组件创建工具提示"""
        # 这里可以使用tkinter的tooltip库或自定义tooltip
        # 例如为工具按钮添加tooltip
        pass
    
    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
    
    def select_preset_color(self, color):
        """选择预设颜色"""
        self.current_color = color
        self.color_preview.config(bg=color)
        # 如果字体预览存在，也更新字体颜色
        if hasattr(self, 'font_preview'):
            self.font_preview.config(foreground=color)
    
    def adjust_font_size(self, change):
        """调整字体大小"""
        try:
            new_size = max(8, min(72, self.font_size + change))
            self.font_size = new_size
            self.font_size_var.set(str(new_size))
            # 更新预览
            self.font_preview.config(font=("微软雅黑", new_size))
        except:
            pass
    
    def on_font_size_change(self, event=None):
        """字体大小改变处理"""
        try:
            size = int(self.font_size_var.get())
            if 8 <= size <= 72:
                self.font_size = size
                # 更新预览
                self.font_preview.config(font=("微软雅黑", size))
            else:
                self.font_size_var.set(str(self.font_size))
        except ValueError:
            self.font_size_var.set(str(self.font_size))
    
    def on_mosaic_size_spin(self):
        try:
            size = int(self.mosaic_size_var.get())
            if 5 <= size <= 100:
                self.mosaic_size = size
                self.mosaic_size_scale.set(size)
            else:
                self.mosaic_size_var.set(str(self.mosaic_size))
        except ValueError:
            self.mosaic_size_var.set(str(self.mosaic_size))
    
    def on_mosaic_size_scale(self, value):
        size = int(float(value))
        self.mosaic_size = size
        self.mosaic_size_var.set(size)
    
    def on_tool_change(self):
        self.current_tool = self.tool_var.get()
        # 工具按钮高亮
        for tool, btn in self.tool_btns.items():
            if tool == self.current_tool:
                btn.configure(style="ToolButton.TRadiobutton")
            else:
                btn.configure(style="ToolButton.TRadiobutton")
        # 更新鼠标样式
        if self.current_tool == 'text':
            self.canvas.config(cursor="xterm")
            self.font_size_frame.pack(side=tk.TOP, pady=8, padx=12, fill=tk.X)
            self.mosaic_size_frame.pack_forget()
        elif self.current_tool == 'mosaic':
            self.canvas.config(cursor="crosshair")
            self.font_size_frame.pack_forget()
            self.mosaic_size_frame.pack(side=tk.TOP, pady=8, padx=12, fill=tk.X)
        else:
            self.canvas.config(cursor="cross")
            self.font_size_frame.pack_forget()
            self.mosaic_size_frame.pack_forget()
        self.remove_mosaic_cursor()
    
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_preview.config(bg=color)
        # 恢复窗口最上层
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)
    
    def on_mouse_down(self, event):
        """鼠标按下事件处理"""
        if self.current_tool == 'text':
            if self.text_entry:
                self.canvas.delete(self.text_entry)
            img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
            # 创建更美观的文本输入框
            entry = tk.Entry(
                self.canvas, 
                font=("微软雅黑", self.font_size), 
                fg=self.current_color,
                bd=1,
                relief=tk.SOLID,
                width=20,
                bg="#ffffff" if not self.is_dark_mode else "#333333"
            )
            entry.insert(0, "")
            entry.bind('<Return>', lambda e: self.finish_text_input(e, img_x, img_y))
            entry.bind('<Escape>', lambda e: self.cancel_text_input(e))
            canvas_x, canvas_y = self.image_to_canvas_coords(img_x, img_y)
            self.text_entry = self.canvas.create_window(canvas_x, canvas_y, window=entry)
            entry.focus_set()
            return
        
        img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
        self.rect_start = (img_x, img_y)
        c0, c1 = self.image_to_canvas_coords(img_x, img_y)
        if self.current_tool == 'rect':
            # 创建更粗的矩形轮廓，提高可见度
            self.rect_id = self.canvas.create_rectangle(c0, c1, c0, c1, outline=self.current_color, width=4, tags='preview', activeoutline='', activefill='')
        elif self.current_tool == 'arrow':
            # 创建更粗的箭头线条，提高可见度
            self.rect_id = self.canvas.create_line(c0, c1, c0, c1, fill=self.current_color, width=4, tags='preview', activefill='')
        elif self.current_tool == 'mosaic':
            self.is_mosaic_drawing = True
            self.last_mosaic_point = (img_x, img_y)
            self.apply_mosaic_smear(img_x, img_y)
    
    def on_mouse_move(self, event):
        """鼠标移动事件处理"""
        if self.rect_id and self.rect_start:
            img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
            x0, y0 = self.rect_start
            c0, c1 = self.image_to_canvas_coords(x0, y0)
            c2, c3 = self.image_to_canvas_coords(img_x, img_y)
            if self.current_tool == 'rect':
                self.canvas.coords(self.rect_id, c0, c1, c2, c3)
            elif self.current_tool == 'arrow':
                self.canvas.coords(self.rect_id, c0, c1, c2, c3)
        elif getattr(self, 'is_mosaic_drawing', False) and self.current_tool == 'mosaic':
            img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
            self.apply_mosaic_smear(img_x, img_y)
            self.last_mosaic_point = (img_x, img_y)
            self._last_cursor_pos = (event.x, event.y)
            self.draw_mosaic_cursor(event.x, event.y)
    
    def on_mouse_up(self, event):
        """鼠标释放事件处理"""
        if not self.rect_start and not getattr(self, 'is_mosaic_drawing', False):
            return
        
        if self.current_tool == 'text':
            return
        
        img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
        x1, y1 = self.rect_start if self.rect_start else (img_x, img_y)
        x2, y2 = img_x, img_y
        
        if self.current_tool == 'rect':
            if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
                if self.rect_id:
                    self.canvas.delete(self.rect_id)
                self.rect_start = None
                self.rect_id = None
                return
            # 使用优化的矩形绘制方法
            self.draw_rectangle(x1, y1, x2, y2, self.current_color)
            self.rects.append(('rect', (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)), self.current_color, None))
        elif self.current_tool == 'arrow':
            self.draw_arrow(x1, y1, x2, y2, self.current_color)
            self.rects.append(('arrow', (x1, y1, x2, y2), self.current_color, None))
        elif self.current_tool == 'mosaic':
            if getattr(self, 'is_mosaic_drawing', False):
                self.rects.append(('mosaic_smear', None, None, None))
                self.is_mosaic_drawing = False
                self.last_mosaic_point = None
        # 标注完成后，删除临时预览对象
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        self.update_canvas_image()
        self.rect_start = None
        self.undo_btn.config(state="normal")
        self.clear_btn.config(state="normal")
    
    def finish_text_input(self, event, x, y):
        """完成文字输入"""
        text = event.widget.get()
        if text.strip():
            try:
                # 尝试使用微软雅黑字体
                font = ImageFont.truetype("msyh.ttc", self.font_size)
            except:
                try:
                    # 尝试使用系统默认字体
                    font = ImageFont.truetype("arial.ttf", self.font_size)
                except:
                    # 如果都失败，使用默认字体
                    font = ImageFont.load_default()
            
            # 保存文字
            self.draw.text((x, y), text, fill=self.current_color, font=font)
            self.rects.append(('text', (x, y), self.current_color, text))
            self.update_canvas_image()
            # 启用撤销和清除按钮
            self.undo_btn.config(state="normal")
            self.clear_btn.config(state="normal")
        # 清理输入框
        self.canvas.delete(self.text_entry)
        event.widget.destroy()
        self.text_entry = None
    
    def cancel_text_input(self, event):
        """取消文字输入"""
        self.canvas.delete(self.text_entry)
        event.widget.destroy()
        self.text_entry = None
    
    def undo_last(self):
        """撤销最后一个操作"""
        if self.rects:
            self.rects.pop()  # 移除最后一个操作
            # 重新绘制所有内容
            self.image = self.original_image.copy()
            self.draw = ImageDraw.Draw(self.image)
            for item in self.rects:
                tool_type, coords, color, text = item
                if tool_type == 'rect':
                    # 使用优化的矩形绘制方法
                    x0, y0, x1, y1 = coords
                    self.draw_rectangle(x0, y0, x1, y1, color)
                elif tool_type == 'arrow':
                    self.draw_arrow(*coords, color)
                elif tool_type == 'text':
                    try:
                        font = ImageFont.truetype("msyh.ttc", self.font_size)
                    except:
                        try:
                            font = ImageFont.truetype("arial.ttf", self.font_size)
                        except:
                            font = ImageFont.load_default()
                    self.draw.text(coords, text, fill=color, font=font)
                elif tool_type == 'mosaic':
                    self.apply_mosaic(*coords)
                elif tool_type == 'mosaic_smear':
                    # 对于涂抹类型的马赛克，需要重新加载原图，因为无法精确撤销
                    pass  # 由于已重新开始绘制，不需要额外处理
            
            self.update_canvas_image()
            
            # 如果没有操作了，禁用撤销和清除按钮
            if not self.rects:
                self.undo_btn.config(state="disabled")
                self.clear_btn.config(state="disabled")
    
    def clear_all(self):
        """清除所有标注"""
        if messagebox.askyesno("确认", "确定要清除所有标注吗？"):
            self.rects.clear()
            self.image = self.original_image.copy()
            self.draw = ImageDraw.Draw(self.image)
            # 清除Canvas上所有内容
            self.canvas.delete("all")
            # 重新显示背景图片
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas_img = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.undo_btn.config(state="disabled")
            self.clear_btn.config(state="disabled")
            # 恢复窗口最上层
            self.attributes('-topmost', True)
            self.attributes('-topmost', False)
    
    def update_canvas_image(self):
        """更新画布上的图像并重绘标注"""
        # 提高图像清晰度
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfig(self.canvas_img, image=self.tk_image)
        
        # 先清空所有preview对象，防止重复
        for item in self.canvas.find_withtag('preview'):
            self.canvas.delete(item)
            
        self.redraw_all_annotations()
        
        # 缩放后重绘马赛克提示圈
        if self.current_tool == 'mosaic' and hasattr(self, '_last_cursor_pos'):
            self.draw_mosaic_cursor(*self._last_cursor_pos)
    
    def redraw_all_annotations(self):
        """重绘所有标注，优化线条粗细和颜色对比度"""
        # 清空所有临时预览
        for item in self.canvas.find_withtag('preview'):
            self.canvas.delete(item)
            
        # 确定线宽
        line_width = 4  # 增加线宽以提高可见度
            
        for item in self.rects:
            tool_type, coords, color, text = item
            if tool_type == 'rect':
                x0, y0, x1, y1 = coords
                c0, c1 = self.image_to_canvas_coords(x0, y0)
                c2, c3 = self.image_to_canvas_coords(x1, y1)
                # 增加线宽以提高可见度
                self.canvas.create_rectangle(c0, c1, c2, c3, outline=color, width=line_width, tags='preview', activeoutline='', activefill='')
            elif tool_type == 'arrow':
                x0, y0, x1, y1 = coords
                c0, c1 = self.image_to_canvas_coords(x0, y0)
                c2, c3 = self.image_to_canvas_coords(x1, y1)
                # 增加线宽以提高可见度
                self.canvas.create_line(c0, c1, c2, c3, fill=color, width=line_width, tags='preview', activefill='')
            elif tool_type == 'text':
                x, y = coords
                c0, c1 = self.image_to_canvas_coords(x, y)
                # 增大字体以提高可读性
                font_size = max(self.font_size, 16)
                self.canvas.create_text(c0, c1, text=text, fill=color, font=("微软雅黑", font_size, "bold"), tags='preview')
            # 马赛克等其他类型可按需回显
    
    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG图片', '*.png')])
        if file_path:
            self.image.save(file_path)
            messagebox.showinfo("保存成功", f"图片已保存到：{file_path}")
    
    def finish(self):
        self.result_image = self.image.copy()
        # 关闭前恢复最上层，防止被遮挡
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)
        self.destroy()
    
    def cancel(self):
        self.cancelled = True
        self.destroy()
    
    def get_result(self):
        self.wait_window()
        if self.cancelled:
            return None
        return self.result_image

    def apply_mosaic_smear(self, img_x, img_y):
        """在当前位置涂抹马赛克"""
        size = self.mosaic_size
        x0 = max(0, img_x - size // 2)
        y0 = max(0, img_y - size // 2)
        x1 = min(self.image.width, img_x + size // 2)
        y1 = min(self.image.height, img_y + size // 2)
        region = self.image.crop((x0, y0, x1, y1))
        width, height = region.size
        block_size = max(3, min(size, min(width, height)))
        for i in range(0, width, block_size):
            for j in range(0, height, block_size):
                block = region.crop((i, j, min(i + block_size, width), min(j + block_size, height)))
                avg_color = tuple(map(int, block.resize((1, 1), Image.LANCZOS).getpixel((0, 0))))
                self.draw.rectangle([x0 + i, y0 + j, min(x0 + i + block_size, x1), min(y0 + j + block_size, y1)], fill=avg_color)
        self.update_canvas_image()

    def on_mouse_motion(self, event):
        """鼠标移动时显示马赛克提示圈"""
        if self.current_tool == 'mosaic':
            self._last_cursor_pos = (event.x, event.y)
            self.draw_mosaic_cursor(event.x, event.y)
        else:
            self.remove_mosaic_cursor()
            if hasattr(self, '_last_cursor_pos'):
                del self._last_cursor_pos

    def on_mouse_leave(self, event):
        self.remove_mosaic_cursor()

    def remove_mosaic_cursor(self):
        if self.mosaic_cursor_id:
            self.canvas.delete(self.mosaic_cursor_id)
            self.mosaic_cursor_id = None

    def draw_mosaic_cursor(self, x, y):
        size = self.mosaic_size
        x0, y0 = x - size // 2, y - size // 2
        x1, y1 = x + size // 2, y + size // 2
        self.remove_mosaic_cursor()
        # 使用更美观的虚线样式
        self.mosaic_cursor_id = self.canvas.create_oval(
            x0, y0, x1, y1, 
            outline=self.current_color, 
            width=2, 
            dash=(3,2)
        )

    def on_mouse_enter(self, event):
        self.canvas.focus_set()

    def on_mouse_wheel(self, event):
        # 记录鼠标在画布上的位置
        if hasattr(event, 'x') and hasattr(event, 'y'):
            self._last_wheel_mouse = (event.x, event.y)
        else:
            self._last_wheel_mouse = (self.canvas.winfo_width()//2, self.canvas.winfo_height()//2)
        # 计算缩放因子
        if hasattr(event, 'delta'):
            if event.delta > 0:
                factor = 1.1
            else:
                factor = 0.9
        elif event.num == 4:
            factor = 1.1
        elif event.num == 5:
            factor = 0.9
        else:
            factor = 1.0
        new_scale = self.zoom_scale * factor
        if new_scale < self.min_zoom or new_scale > self.max_zoom:
            return
        self.zoom_scale = new_scale
        self.update_canvas_zoom(center_mouse=True)

    def update_canvas_zoom(self, center_mouse=False):
        # 只缩放显示，不影响原始图片和标注
        w, h = self.image.width, self.image.height
        new_w, new_h = int(w * self.zoom_scale), int(h * self.zoom_scale)
        zoomed_img = self.image.resize((new_w, new_h), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(zoomed_img)
        # 只更新已有的canvas_img，不新建
        self.canvas.itemconfig(self.canvas_img, image=self.tk_image)
        self.canvas.config(width=new_w, height=new_h)
        # 以鼠标为中心缩放
        if center_mouse:
            mx, my = self._last_wheel_mouse
            if self.zoom_scale != 0:
                relx = mx / (w * self.zoom_scale / (self.zoom_scale / 1.1 if hasattr(self, '_last_factor') and self._last_factor > 1 else self.zoom_scale / 0.9))
                rely = my / (h * self.zoom_scale / (self.zoom_scale / 1.1 if hasattr(self, '_last_factor') and self._last_factor > 1 else self.zoom_scale / 0.9))
            else:
                relx, rely = 0, 0
            new_img_x = mx - relx * new_w
            new_img_y = my - rely * new_h
            new_img_x = min(0, max(self.canvas.winfo_width() - new_w, new_img_x))
            new_img_y = min(0, max(self.canvas.winfo_height() - new_h, new_img_y))
            self.canvas.coords(self.canvas_img, new_img_x, new_img_y)
        else:
            self.canvas.coords(self.canvas_img, 0, 0)
        # 清空所有preview对象，防止重复
        for item in self.canvas.find_withtag('preview'):
            self.canvas.delete(item)
        self.redraw_all_annotations()
        # 缩放后重绘马赛克提示圈
        if self.current_tool == 'mosaic' and hasattr(self, '_last_cursor_pos'):
            self.draw_mosaic_cursor(*self._last_cursor_pos) 

    def draw_arrow(self, x1, y1, x2, y2, color):
        """绘制箭头"""
        # 计算箭头角度
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_length = 20  # 箭头长度
        arrow_angle = math.pi / 6  # 箭头角度（30度）
        
        # 计算箭头两个点
        x3 = x2 - arrow_length * math.cos(angle + arrow_angle)
        y3 = y2 - arrow_length * math.sin(angle + arrow_angle)
        x4 = x2 - arrow_length * math.cos(angle - arrow_angle)
        y4 = y2 - arrow_length * math.sin(angle - arrow_angle)
        
        # 特殊处理白色标注，添加黑色边框辅助
        if color.upper() == '#FFFFFF':
            # 先绘制黑色线条
            self.draw.line([x1, y1, x2, y2], fill='#000000', width=6)
            self.draw.line([x2, y2, x3, y3], fill='#000000', width=6)
            self.draw.line([x2, y2, x4, y4], fill='#000000', width=6)
            self.draw.line([x3, y3, x4, y4], fill='#000000', width=6)
        
        # 绘制箭头线 - 增加线宽以提高可见度
        self.draw.line([x1, y1, x2, y2], fill=color, width=4)
        # 绘制箭头
        self.draw.line([x2, y2, x3, y3], fill=color, width=4)
        self.draw.line([x2, y2, x4, y4], fill=color, width=4)
        
        # 确保箭头不会被覆盖
        self.draw.line([x3, y3, x4, y4], fill=color, width=4)
    
    def apply_mosaic(self, x1, y1, x2, y2):
        """应用马赛克效果"""
        # 获取区域图像
        region = self.image.crop((x1, y1, x2, y2))
        width, height = region.size
        
        # 确保马赛克块大小合适
        block_size = max(5, min(self.mosaic_size, min(width, height) // 4))
        
        # 创建马赛克效果
        for i in range(0, width, block_size):
            for j in range(0, height, block_size):
                # 获取块的平均颜色
                block = region.crop((i, j, min(i + block_size, width), 
                                  min(j + block_size, height)))
                # 缩小到1x1获取平均颜色
                avg_color = tuple(map(int, block.resize((1, 1), Image.LANCZOS).getpixel((0, 0))))
                # 填充块
                self.draw.rectangle([x1 + i, y1 + j, 
                                   min(x1 + i + block_size, x2),
                                   min(y1 + j + block_size, y2)],
                                  fill=avg_color)
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        # 获取当前图片在canvas上的偏移
        img_coords = self.canvas.coords(self.canvas_img)
        if img_coords:
            img_offset_x, img_offset_y = img_coords[0], img_coords[1]
        else:
            img_offset_x, img_offset_y = 0, 0
        img_x = (canvas_x - img_offset_x) / self.zoom_scale
        img_y = (canvas_y - img_offset_y) / self.zoom_scale
        return int(img_x), int(img_y)

    def image_to_canvas_coords(self, img_x, img_y):
        img_coords = self.canvas.coords(self.canvas_img)
        if img_coords:
            img_offset_x, img_offset_y = img_coords[0], img_coords[1]
        else:
            img_offset_x, img_offset_y = 0, 0
        canvas_x = img_x * self.zoom_scale + img_offset_x
        canvas_y = img_y * self.zoom_scale + img_offset_y
        return int(canvas_x), int(canvas_y)

    def draw_rectangle(self, x0, y0, x1, y1, color):
        """绘制矩形，提高对比度和可见度"""
        # 确保坐标正确排序
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        
        # 增加线宽以提高可见度
        line_width = 4
        
        # 特殊处理白色标注，添加黑色边框辅助
        if color.upper() == '#FFFFFF':
            # 先绘制黑色外边框
            outer_border = 1  # 外边框宽度
            self.draw.rectangle([x0-outer_border, y0-outer_border, x1+outer_border, y1+outer_border], outline='#000000', width=line_width)
        
        # 绘制更粗的矩形边框
        self.draw.rectangle([x0, y0, x1, y1], outline=color, width=line_width)
        
        # 如果是表格区域（较大矩形），添加淡色填充以增强可见度
        if abs(x1 - x0) > 100 and abs(y1 - y0) > 100:
            # 创建半透明填充色
            fill_color = self.get_highlight_color(color)
            # 绘制内部填充（稍微缩小以不覆盖边框）
            inner_x0, inner_y0 = x0 + line_width, y0 + line_width
            inner_x1, inner_y1 = x1 - line_width, y1 - line_width
            # 使用alpha通道创建半透明填充
            overlay = Image.new('RGBA', self.image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([inner_x0, inner_y0, inner_x1, inner_y1], fill=fill_color)
            
            # 将overlay合并到原图
            if self.image.mode != 'RGBA':
                self.image = self.image.convert('RGBA')
            self.image = Image.alpha_composite(self.image, overlay)
            self.draw = ImageDraw.Draw(self.image)
    
    def get_highlight_color(self, color):
        """根据线条颜色获取适合的半透明填充色"""
        # 将HEX颜色转换为RGB
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            # 创建半透明版本 (r,g,b,alpha)，alpha为60表示透明度约75%
            return (r, g, b, 60)
        return (255, 255, 255, 40)  # 默认为半透明白色 