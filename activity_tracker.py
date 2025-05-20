import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab, Image, ImageTk
import datetime
import os
import pyautogui
import time

class ActivityTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("留痕软件")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 创建保存截图的文件夹
        self.screenshot_dir = "screenshots"
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TEntry", font=("微软雅黑", 10))
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 时间显示
        self.time_frame = ttk.Frame(self.main_frame)
        self.time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.time_frame, text="当前时间:", font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT)
        self.time_label = ttk.Label(self.time_frame, text="", font=("微软雅黑", 10))
        self.time_label.pack(side=tk.LEFT, padx=5)
        self.update_time()
        
        # 项目/事务输入
        self.task_frame = ttk.Frame(self.main_frame)
        self.task_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.task_frame, text="项目/事务:", font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT)
        self.task_entry = ttk.Entry(self.task_frame, width=50, font=("微软雅黑", 10))
        self.task_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 截图预览区域
        self.preview_frame = ttk.LabelFrame(self.main_frame, text="截图预览", padding="5")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 按钮区域
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        self.screenshot_btn = ttk.Button(self.button_frame, text="截图", command=self.take_screenshot)
        self.screenshot_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(self.button_frame, text="保存", command=self.save_screenshot)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.save_btn.config(state="disabled")  # 初始状态禁用
        
        self.clear_btn = ttk.Button(self.button_frame, text="清除", command=self.clear_screenshot)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        self.clear_btn.config(state="disabled")  # 初始状态禁用
        
        # 截图相关变量
        self.current_screenshot = None
        self.screenshot_preview = None
    
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # 每秒更新一次
    
    def take_screenshot(self):
        """捕获屏幕截图"""
        # 最小化窗口以便截图不包含本应用
        self.root.iconify()
        # 等待一小段时间以确保窗口已最小化
        time.sleep(0.5)
        
        # 捕获全屏截图
        self.current_screenshot = pyautogui.screenshot()
        
        # 恢复窗口
        self.root.deiconify()
        
        # 调整图像大小以适应预览区域
        self.display_screenshot()
        
        # 启用保存和清除按钮
        self.save_btn.config(state="normal")
        self.clear_btn.config(state="normal")
    
    def display_screenshot(self):
        """在预览区域显示截图"""
        if self.current_screenshot:
            # 获取预览区域的大小
            preview_width = self.preview_frame.winfo_width()
            preview_height = self.preview_frame.winfo_height()
            
            # 确保尺寸至少为1像素
            preview_width = max(1, preview_width - 10)  # 减去padding
            preview_height = max(1, preview_height - 10)  # 减去padding
            
            # 调整图像大小以适应预览区域，保持纵横比
            img_width, img_height = self.current_screenshot.size
            ratio = min(preview_width/img_width, preview_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            resized_img = self.current_screenshot.resize((new_width, new_height), Image.LANCZOS)
            self.screenshot_preview = ImageTk.PhotoImage(resized_img)
            
            # 更新预览标签
            self.preview_label.config(image=self.screenshot_preview)
    
    def save_screenshot(self):
        """保存截图"""
        if not self.current_screenshot:
            messagebox.showerror("错误", "没有可保存的截图")
            return
        
        task = self.task_entry.get().strip()
        if not task:
            messagebox.showerror("错误", "请输入项目/事务名称")
            return
        
        # 生成文件名：时间_项目名称.png
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # 替换文件名中不允许的字符
        safe_task = "".join([c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in task])
        filename = f"{timestamp}_{safe_task}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        # 保存截图
        self.current_screenshot.save(filepath)
        messagebox.showinfo("成功", f"截图已保存为：{filename}")
    
    def clear_screenshot(self):
        """清除当前截图"""
        self.current_screenshot = None
        self.screenshot_preview = None
        self.preview_label.config(image="")
        self.save_btn.config(state="disabled")
        self.clear_btn.config(state="disabled")

    def on_resize(self, event):
        """窗口大小改变时调整预览图像"""
        if self.current_screenshot:
            self.display_screenshot()

if __name__ == "__main__":
    root = tk.Tk()
    app = ActivityTracker(root)
    
    # 绑定窗口大小改变事件
    root.bind("<Configure>", app.on_resize)
    
    root.mainloop()