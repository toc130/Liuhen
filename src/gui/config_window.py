"""
配置窗口 - 用户可修改应用配置
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import os
import json
import sys
import copy

from src.utils.theme_manager import ThemedWindow
from src.utils.config_manager import default_config_manager
from src.config import (
    APP_NAME, APP_VERSION,
    UI_FONT_BOLD, UI_FONT_NORMAL, UI_FONT_LARGE,
    INTERVAL_REMINDER_MINUTES, DEFAULT_REMINDER_TIME,
    REMINDER_MESSAGE, INTERVAL_REMINDER_MESSAGE,
    REMINDER_SOUND_ENABLED, SCREENSHOT_DIR
)

class ConfigWindow(ThemedWindow):
    """配置窗口类"""
    
    def __init__(self, parent, callback=None):
        """初始化配置窗口
        
        Args:
            parent: 父窗口
            callback: 配置更改回调函数
        """
        super().__init__(parent, f"{APP_NAME} - 应用设置")
        
        # 窗口设置 - 增加高度
        self.geometry("1000x750")
        self.resizable(True, True)
        self.minsize(500, 450)
        
        # 配置管理器
        self.config_manager = default_config_manager
        
        # 保存回调函数
        self.callback = callback
        
        # 加载当前配置并确保所有需要的配置部分都存在
        self.config_values = self.config_manager.config.copy()
        
        # 确保files配置部分存在
        if "files" not in self.config_values:
            self.config_values["files"] = {
                "screenshot_save_path": SCREENSHOT_DIR,
                "use_custom_path": False
            }
        
        # 创建配置界面
        self.create_widgets()
        
        # 居中显示
        self.center_window()
        
        # 设置模态窗口
        self.transient(parent)
        self.grab_set()
        self.focus_set()
    
    def center_window(self):
        """窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建配置界面组件"""
        # 使用主题管理器的样式
        style = self.create_themed_style()
        
        # 创建顶部标题
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        ttk.Label(
            title_frame, 
            text="应用设置", 
            font=UI_FONT_LARGE
        ).pack(side=tk.LEFT)
        
        # 创建主框架，用于容纳选项卡和按钮
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
        
        # 创建选项卡面板
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建提醒设置选项卡
        reminder_frame = self.create_reminder_settings(notebook)
        notebook.add(reminder_frame, text="提醒设置")
        
        # 创建界面设置选项卡
        ui_frame = self.create_ui_settings(notebook)
        notebook.add(ui_frame, text="界面设置")
        
        # 创建文件设置选项卡
        files_frame = self.create_files_settings(notebook)
        notebook.add(files_frame, text="文件设置")
        
        # 创建高级设置选项卡
        advanced_frame = self.create_advanced_settings(notebook)
        notebook.add(advanced_frame, text="高级设置")
        
        # 创建底部按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="取消",
            command=self.destroy,
            width=10
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="保存",
            style="Primary.TButton",
            command=self.save_config,
            width=10
        ).pack(side=tk.RIGHT)
        
        # 添加恢复默认设置按钮
        self.reset_btn = ttk.Button(
            button_frame,
            text="恢复默认",
            command=self.reset_defaults,
            width=12
        )
        self.reset_btn.pack(side=tk.LEFT)
        
        # 验证按钮事件绑定
        print(f"恢复默认按钮绑定到: {self.reset_defaults.__name__}")
    
    def create_reminder_settings(self, parent):
        """创建提醒设置面板
        
        Args:
            parent: 父容器
        
        Returns:
            ttk.Frame: 设置面板
        """
        frame = ttk.Frame(parent, padding=10)
        
        # 默认提醒时间
        time_frame = ttk.Frame(frame)
        time_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(
            time_frame, 
            text="默认提醒时间:", 
            font=UI_FONT_BOLD
        ).pack(side=tk.LEFT, anchor='w')
        
        self.reminder_time_var = tk.StringVar(value=self.config_values["reminder"]["default_time"])
        time_entry = ttk.Entry(
            time_frame, 
            textvariable=self.reminder_time_var,
            width=10
        )
        time_entry.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(
            time_frame,
            text="格式: HH:MM (24小时制)"
        ).pack(side=tk.LEFT)
        
        # 提醒消息
        message_frame = ttk.Frame(frame)
        message_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(
            message_frame,
            text="提醒消息:",
            font=UI_FONT_BOLD
        ).pack(anchor='w')
        
        self.reminder_message_var = tk.StringVar(value=self.config_values["reminder"]["message"])
        message_entry = ttk.Entry(
            message_frame,
            textvariable=self.reminder_message_var
        )
        message_entry.pack(fill=tk.X, pady=2)
        
        # 启用声音提醒
        sound_frame = ttk.Frame(frame)
        sound_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.sound_enabled_var = tk.BooleanVar(value=self.config_values["reminder"]["sound_enabled"])
        sound_check = ttk.Checkbutton(
            sound_frame,
            text="启用声音提醒",
            variable=self.sound_enabled_var
        )
        sound_check.pack(anchor='w')
        
        # 间隔提醒设置
        interval_frame = ttk.Frame(frame)
        interval_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(
            interval_frame,
            text="间隔提醒时间(分钟):",
            font=UI_FONT_BOLD
        ).pack(side=tk.LEFT, anchor='w')
        
        self.interval_min_var = tk.IntVar(value=self.config_values["reminder"]["interval_minutes"])
        interval_entry = ttk.Spinbox(
            interval_frame,
            from_=1,
            to=60,
            textvariable=self.interval_min_var,
            width=5
        )
        interval_entry.pack(side=tk.LEFT, padx=10)
        
        # 间隔提醒消息
        interval_msg_frame = ttk.Frame(frame)
        interval_msg_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(
            interval_msg_frame,
            text="间隔提醒消息:",
            font=UI_FONT_BOLD
        ).pack(anchor='w')
        
        self.interval_message_var = tk.StringVar(value=self.config_values["reminder"]["interval_message"])
        interval_msg_entry = ttk.Entry(
            interval_msg_frame,
            textvariable=self.interval_message_var
        )
        interval_msg_entry.pack(fill=tk.X, pady=2)
        
        return frame
    
    def create_ui_settings(self, parent):
        """创建界面设置面板
        
        Args:
            parent: 父容器
        
        Returns:
            ttk.Frame: 设置面板
        """
        frame = ttk.Frame(parent, padding=10)
        
        # 启动时最大化
        self.maximize_var = tk.BooleanVar(value=self.config_values["ui"]["startup_maximized"])
        maximize_check = ttk.Checkbutton(
            frame,
            text="启动时最大化窗口",
            variable=self.maximize_var
        )
        maximize_check.pack(anchor='w', pady=(0, 5))
        
        # 退出时确认
        self.confirm_exit_var = tk.BooleanVar(value=self.config_values["ui"]["confirm_on_exit"])
        confirm_check = ttk.Checkbutton(
            frame,
            text="退出时显示确认对话框",
            variable=self.confirm_exit_var
        )
        confirm_check.pack(anchor='w', pady=(0, 5))
        
        # 自动保存截图
        self.auto_save_var = tk.BooleanVar(value=self.config_values["ui"]["auto_save"])
        auto_save_check = ttk.Checkbutton(
            frame,
            text="截图后自动保存 (需要输入事务名称)",
            variable=self.auto_save_var
        )
        auto_save_check.pack(anchor='w', pady=(0, 5))
        
        # 截图质量设置
        quality_frame = ttk.Frame(frame)
        quality_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            quality_frame,
            text="截图质量:",
            font=UI_FONT_BOLD
        ).pack(side=tk.LEFT)
        
        self.quality_var = tk.IntVar(value=self.config_values["ui"]["screenshot_quality"])
        quality_scale = ttk.Scale(
            quality_frame,
            from_=10,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.quality_var,
            length=200
        )
        quality_scale.pack(side=tk.LEFT, padx=10)
        
        quality_label = ttk.Label(quality_frame, text=f"{self.quality_var.get()}%")
        quality_label.pack(side=tk.LEFT)
        
        # 更新质量标签
        def update_quality_label(*args):
            quality_label.config(text=f"{self.quality_var.get()}%")
        
        self.quality_var.trace_add("write", update_quality_label)
        
        return frame
    
    def create_files_settings(self, parent):
        """创建文件设置面板
        
        Args:
            parent: 父容器
        
        Returns:
            ttk.Frame: 设置面板
        """
        # 创建带滚动条的框架
        container = ttk.Frame(parent)
        
        # 创建Canvas和滚动条
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # 配置Canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建内容框架
        frame = ttk.Frame(canvas, padding=10)
        
        # 将框架放入Canvas
        canvas_frame = canvas.create_window((0, 0), window=frame, anchor="nw")
        
        # 配置Canvas大小
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 设置Canvas的宽度跟随frame
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=canvas.winfo_width()))
        
        # 使用自定义保存路径
        use_custom_path_frame = ttk.Frame(frame)
        use_custom_path_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.use_custom_path_var = tk.BooleanVar(value=self.config_values["files"]["use_custom_path"])
        use_custom_path_check = ttk.Checkbutton(
            use_custom_path_frame,
            text="使用自定义保存路径",
            variable=self.use_custom_path_var,
            command=self.toggle_path_entry
        )
        use_custom_path_check.pack(anchor='w')
        
        # 显示默认保存路径
        default_path_frame = ttk.Frame(frame)
        default_path_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            default_path_frame,
            text="默认保存路径:",
            font=UI_FONT_BOLD
        ).pack(side=tk.LEFT, anchor='w')
        
        # 显示SCREENSHOT_DIR的值
        default_path_label = ttk.Label(
            default_path_frame,
            text=SCREENSHOT_DIR,
            style="Info.TLabel"
        )
        default_path_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # 截图保存路径
        self.path_frame = ttk.Frame(frame)
        self.path_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(
            self.path_frame,
            text="自定义保存路径:",
            font=UI_FONT_BOLD
        ).pack(side=tk.LEFT, anchor='w')
        
        self.screenshot_dir_var = tk.StringVar(value=self.config_values["files"]["screenshot_save_path"])
        self.path_entry = ttk.Entry(
            self.path_frame,
            textvariable=self.screenshot_dir_var,
            width=30
        )
        self.path_entry.pack(side=tk.LEFT, padx=10)
        
        # 添加文件夹选择按钮
        self.browse_button = ttk.Button(
            self.path_frame,
            text="浏览",
            command=self.browse_screenshot_dir
        )
        self.browse_button.pack(side=tk.LEFT)
        
        # 添加路径说明
        path_note_frame = ttk.Frame(frame)
        path_note_frame.pack(fill=tk.X, pady=(2, 5))
        
        ttk.Label(
            path_note_frame,
            text="注意: 修改保存路径后，新的截图将保存到指定位置，但旧的截图不会迁移。",
            wraplength=400,
            justify=tk.LEFT,
            style="Small.TLabel"
        ).pack(fill=tk.X)
        
        # 添加打包环境路径提示
        packaged_note_frame = ttk.Frame(frame)
        packaged_note_frame.pack(fill=tk.X, pady=(0, 5))
        
        packaged_note = ttk.Label(
            packaged_note_frame,
            text="打包说明: 当软件打包为exe运行时，默认保存路径在您的个人目录下的.liuhen文件夹中。"
                 "建议使用绝对路径作为自定义路径，例如D:\\Screenshots或C:\\Users\\用户名\\Pictures\\留痕截图。",
            wraplength=400,
            justify=tk.LEFT,
            style="Small.TLabel"
        )
        packaged_note.pack(fill=tk.X)
        
        # 初始化控件状态
        self.toggle_path_entry()
        
        return container
    
    def toggle_path_entry(self):
        """启用或禁用路径输入控件"""
        state = "normal" if self.use_custom_path_var.get() else "disabled"
        self.path_entry.config(state=state)
        self.browse_button.config(state=state)
    
    def create_advanced_settings(self, parent):
        """创建高级设置面板
        
        Args:
            parent: 父容器
        
        Returns:
            ttk.Frame: 设置面板
        """
        frame = ttk.Frame(parent, padding=10)
        
        # 调试模式
        self.debug_var = tk.BooleanVar(value=self.config_values["advanced"]["debug_mode"])
        debug_check = ttk.Checkbutton(
            frame,
            text="启用调试模式",
            variable=self.debug_var
        )
        debug_check.pack(anchor='w', pady=(0, 5))
        
        # 保存日志
        self.save_log_var = tk.BooleanVar(value=self.config_values["advanced"]["save_logs"])
        log_check = ttk.Checkbutton(
            frame,
            text="保存应用日志",
            variable=self.save_log_var
        )
        log_check.pack(anchor='w', pady=(0, 5))
        
        # 添加一条提示信息
        note_frame = ttk.Frame(frame)
        note_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            note_frame,
            text="注意: 修改高级设置可能会影响应用的稳定性。",
            foreground="red"
        ).pack()
        
        return frame
    
    def browse_screenshot_dir(self):
        """打开文件夹选择对话框"""
        dir_path = filedialog.askdirectory()
        if dir_path:
            # 标准化路径格式
            dir_path = os.path.normpath(dir_path)
            self.screenshot_dir_var.set(dir_path)
            
            # 检查目录是否存在，如果不存在则提示
            if not os.path.exists(dir_path):
                if messagebox.askyesno("目录不存在", 
                                      f"目录 '{dir_path}' 不存在，是否创建此目录？"):
                    try:
                        os.makedirs(dir_path, exist_ok=True)
                        messagebox.showinfo("成功", f"已创建目录: {dir_path}")
                    except Exception as e:
                        messagebox.showerror("错误", f"无法创建目录: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            print("开始保存配置...")
            # 验证自定义路径
            if self.use_custom_path_var.get():
                path = self.screenshot_dir_var.get().strip()
                if not path:
                    messagebox.showerror("错误", "自定义保存路径不能为空")
                    return
                    
                # 检查路径是否存在，如果不存在则提示创建
                if not os.path.exists(path):
                    if messagebox.askyesno("目录不存在", 
                                          f"目录 '{path}' 不存在，是否创建此目录？"):
                        try:
                            os.makedirs(path, exist_ok=True)
                            print(f"已创建目录: {path}")
                        except Exception as e:
                            messagebox.showerror("错误", f"无法创建目录: {e}")
                            return
                    else:
                        messagebox.showinfo("提示", "已取消保存")
                        return
            
            # 更新配置字典
            print("更新配置字典...")
            self.config_values["reminder"]["default_time"] = self.reminder_time_var.get()
            self.config_values["reminder"]["message"] = self.reminder_message_var.get()
            self.config_values["reminder"]["sound_enabled"] = self.sound_enabled_var.get()
            self.config_values["reminder"]["interval_minutes"] = self.interval_min_var.get()
            self.config_values["reminder"]["interval_message"] = self.interval_message_var.get()
            
            self.config_values["ui"]["startup_maximized"] = self.maximize_var.get()
            self.config_values["ui"]["confirm_on_exit"] = self.confirm_exit_var.get()
            self.config_values["ui"]["auto_save"] = self.auto_save_var.get()
            self.config_values["ui"]["screenshot_quality"] = self.quality_var.get()
            
            self.config_values["files"]["use_custom_path"] = self.use_custom_path_var.get()
            # 标准化路径格式
            self.config_values["files"]["screenshot_save_path"] = os.path.normpath(self.screenshot_dir_var.get())
            
            self.config_values["advanced"]["debug_mode"] = self.debug_var.get()
            self.config_values["advanced"]["save_logs"] = self.save_log_var.get()
            
            # 使用配置管理器保存
            print("调用配置管理器保存配置...")
            save_result = self.config_manager.save_config(self.config_values)
            if save_result:
                print("配置保存成功")
                messagebox.showinfo("保存成功", "配置已保存，部分设置将在下次启动应用时生效。")
                
                # 如果有回调函数，则调用
                if self.callback:
                    print("调用配置更改回调函数")
                    self.callback(self.config_values)
                    
                self.destroy()
            else:
                print("配置保存失败")
                messagebox.showerror("保存失败", "无法保存配置，请检查文件权限。")
        except Exception as e:
            print(f"保存配置时发生错误: {e}")
            messagebox.showerror("错误", f"保存配置时发生错误: {e}")
    
    def reset_defaults(self):
        """恢复默认设置"""
        try:
            if messagebox.askyesno("确认", "确定要恢复默认设置吗？"):
                print("正在恢复默认设置...")
                # 重置为默认值，使用深拷贝避免引用问题
                self.config_values = copy.deepcopy(self.config_manager.default_config)
                
                # 更新UI控件的值
                print("更新UI控件值...")
                try:
                    # 设置提醒相关控件
                    print(f"设置提醒时间: {self.config_values['reminder']['default_time']}")
                    self.reminder_time_var.set(self.config_values["reminder"]["default_time"])
                    self.reminder_message_var.set(self.config_values["reminder"]["message"])
                    self.sound_enabled_var.set(self.config_values["reminder"]["sound_enabled"])
                    self.interval_min_var.set(self.config_values["reminder"]["interval_minutes"])
                    self.interval_message_var.set(self.config_values["reminder"]["interval_message"])
                    
                    # 设置UI相关控件
                    print(f"设置UI选项: 最大化={self.config_values['ui']['startup_maximized']}")
                    self.maximize_var.set(self.config_values["ui"]["startup_maximized"])
                    self.confirm_exit_var.set(self.config_values["ui"]["confirm_on_exit"])
                    self.auto_save_var.set(self.config_values["ui"]["auto_save"])
                    self.quality_var.set(self.config_values["ui"]["screenshot_quality"])
                    
                    # 重置文件设置
                    print(f"设置文件选项: 使用自定义路径={self.config_values['files']['use_custom_path']}")
                    self.use_custom_path_var.set(self.config_values["files"]["use_custom_path"])
                    self.screenshot_dir_var.set(self.config_values["files"]["screenshot_save_path"])
                    
                    # 重置高级设置
                    print(f"设置高级选项: 调试模式={self.config_values['advanced']['debug_mode']}")
                    self.debug_var.set(self.config_values["advanced"]["debug_mode"])
                    self.save_log_var.set(self.config_values["advanced"]["save_logs"])
                    
                    # 更新控件状态
                    print("更新控件状态...")
                    self.toggle_path_entry()  # 更新路径输入控件状态
                    
                    # 强制更新UI
                    self.update_idletasks()
                    
                    print("已恢复默认设置")
                    messagebox.showinfo("成功", "已恢复默认设置")
                except Exception as e:
                    print(f"更新UI控件时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("错误", f"更新UI控件时出错: {e}")
            else:
                print("用户取消了恢复默认设置")
        except Exception as e:
            print(f"恢复默认设置时发生错误: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"恢复默认设置时发生错误: {e}") 