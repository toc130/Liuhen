"""
记录查询界面模块 - 实现记录的查询和编辑功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
from PIL import Image, ImageTk

from src.config import (
    UI_FONT_BOLD, UI_FONT_NORMAL, TABLE_COLUMNS, SCREENSHOT_DIR,
    COLOR_PRIMARY, COLOR_BACKGROUND, COLOR_NEUTRAL, 
    DARK_COLOR_PRIMARY, DARK_COLOR_BACKGROUND, DARK_COLOR_NEUTRAL
)
from src.utils.data_manager import DataManager
from src.utils.screenshot import load_image_from_path

# 创建数据管理器实例
data_manager = DataManager()

class RecordsView:
    """记录查询界面类"""
    
    def __init__(self, parent):
        """初始化记录查询界面
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.window = tk.Toplevel(parent.root if hasattr(parent, 'root') else parent)
        self.window.title("查询记录")
        self.window.geometry("900x600")
        self.window.minsize(800, 500)
        self.window.state('zoomed')  # 启动时最大化
        # self.window.transient(parent)  # 注释掉或删除
        self.window.grab_set()           # 保持模态
        self.window.resizable(True, True)
        self.center_window(900, 600)
        
        # 继承父窗口的主题设置
        self.is_dark_mode = False
        if hasattr(parent, 'is_dark_mode'):
            self.is_dark_mode = parent.is_dark_mode
            
        # 获取主题颜色
        self.theme_colors = self.get_theme_colors()
        
        # 设置窗口背景色
        self.window.configure(bg=self.theme_colors["background"])
        
        # 在窗口中存储对自身的引用，方便主窗口访问
        self.window._records_view = self
        
        # 设置样式
        self._setup_styles()
        
        # 当前选中的记录
        self.selected_record = None
        self.current_image = None
        self.image_preview = None
        
        # 创建界面
        self._create_widgets()
        
        # 加载记录
        self._load_records()
    
    def get_theme_colors(self):
        """获取当前主题颜色"""
        if self.is_dark_mode:
            return {
                "background": DARK_COLOR_BACKGROUND,
                "text": DARK_COLOR_NEUTRAL,
                "secondary_text": "#aaaaaa",
                "button_bg": "#333350",  
                "button_active": "#444470",
                "treeview_bg": "#252540",
                "treeview_selected_bg": "#3a3a5e",
                "treeview_selected_fg": "#ffffff",
                "entry_bg": "#333350",
                "entry_fg": "#ffffff",
                "preview_bg": "#2d2d44",
                "border": "#444444"
            }
        else:
            return {
                "background": COLOR_BACKGROUND,
                "text": COLOR_NEUTRAL,
                "secondary_text": "#888888",
                "button_bg": "#f0f0f0",
                "button_active": "#e0e0e0",
                "treeview_bg": "#ffffff",
                "treeview_selected_bg": "#e6f7ff",
                "treeview_selected_fg": "#222222",
                "entry_bg": "#ffffff",
                "entry_fg": "#333333",
                "preview_bg": "#f9f9f9",
                "border": "#dddddd"
            }
    
    def _setup_styles(self):
        style = ttk.Style(self.window)
        style.theme_use('clam')
        
        # 配置Frame样式
        style.configure("TFrame", background=self.theme_colors["background"])
        
        # 配置LabelFrame样式
        style.configure("TLabelframe", 
                      background=self.theme_colors["background"], 
                      font=("微软雅黑", 12, "bold"), 
                      padding=12)
        
        style.configure("TLabelframe.Label", 
                      background=self.theme_colors["background"], 
                      foreground=self.theme_colors["text"],
                      font=("微软雅黑", 12, "bold"))
        
        # 配置Label样式
        style.configure("TLabel", 
                      background=self.theme_colors["background"], 
                      foreground=self.theme_colors["text"],
                      font=("微软雅黑", 12))
        
        # 配置按钮样式
        style.configure("TButton", 
                      font=("微软雅黑", 12), 
                      padding=8,
                      background=self.theme_colors["button_bg"],
                      foreground=self.theme_colors["text"])
        
        style.map("TButton",
                background=[('active', self.theme_colors["button_active"])],
                foreground=[('active', self.theme_colors["text"])])
        
        # 配置Entry样式
        style.configure('TEntry', 
                      padding=5,
                      fieldbackground=self.theme_colors["entry_bg"],
                      foreground=self.theme_colors["entry_fg"])
        
        # 分隔线样式
        style.configure("TSeparator", 
                      background="#ddd" if not self.is_dark_mode else "#444")
        
        # 配置Treeview样式
        style.configure("Treeview", 
                      font=("微软雅黑", 14), 
                      rowheight=40, 
                      fieldbackground=self.theme_colors["treeview_bg"], 
                      background=self.theme_colors["treeview_bg"],
                      foreground=self.theme_colors["text"])
        
        # 设置表头样式
        style.configure("Treeview.Heading", 
                      font=("微软雅黑", 14, "bold"), 
                      background=self.theme_colors["button_bg"],
                      foreground=self.theme_colors["text"],
                      relief="raised",
                      padding=5)
        
        # 设置选中行样式
        style.map("Treeview", 
                background=[('selected', self.theme_colors["treeview_selected_bg"])], 
                foreground=[('selected', self.theme_colors["treeview_selected_fg"])])
        
        # 设置预览标签样式
        style.configure("Preview.TLabel",
                      background=self.theme_colors["preview_bg"],
                      foreground=self.theme_colors["secondary_text"],
                      font=("微软雅黑", 14),
                      padding=15,
                      borderwidth=2,
                      relief="groove")
        
        # 设置滚动条样式
        style.configure("Vertical.TScrollbar", 
                      background=self.theme_colors["button_bg"],
                      troughcolor=self.theme_colors["background"],
                      bordercolor=self.theme_colors["border"],
                      arrowcolor=self.theme_colors["text"])
    
    def center_window(self, width, height):
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 筛选区
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 添加明显的标题
        header_frame = ttk.Frame(filter_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(
            header_frame, 
            text="查询记录", 
            font=("微软雅黑", 16, "bold"),
            foreground=self.theme_colors["text"]
        ).pack(side=tk.LEFT)
        
        # 筛选控件区域
        controls_frame = ttk.Frame(filter_frame)
        controls_frame.pack(fill=tk.X)
        
        # 使用Grid布局，让控件对齐
        ttk.Label(controls_frame, text="关键词:").grid(row=0, column=0, sticky="e", padx=(0, 5), pady=5)
        self.filter_entry = ttk.Entry(controls_frame, width=20)
        self.filter_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(controls_frame, text="开始日期:").grid(row=0, column=2, sticky="e", padx=(15, 5), pady=5)
        self.filter_start = ttk.Entry(controls_frame, width=12)
        self.filter_start.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        ttk.Label(controls_frame, text="结束日期:").grid(row=0, column=4, sticky="e", padx=(15, 5), pady=5)
        self.filter_end = ttk.Entry(controls_frame, width=12)
        self.filter_end.grid(row=0, column=5, sticky="ew", padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(controls_frame)
        button_frame.grid(row=0, column=6, columnspan=2, padx=15, pady=5, sticky="e")
        
        filter_btn = ttk.Button(button_frame, text="筛选", command=self._filter_records, width=8)
        filter_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(button_frame, text="导出CSV", command=self._export_csv, width=10)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # 设置权重，使右侧空间更大
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(3, weight=1)
        controls_frame.columnconfigure(5, weight=1)
        controls_frame.columnconfigure(6, weight=2)
        
        # 主体区
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
        
        list_frame = ttk.Frame(paned_window, padding=5)
        paned_window.add(list_frame, weight=1)
        
        details_frame = ttk.Frame(paned_window, padding=5)
        paned_window.add(details_frame, weight=2)
        
        self._create_records_list(list_frame)
        
        # 分隔线
        sep = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=8)
        
        self._create_details_view(details_frame)
        
        # 底部按钮区
        button_frame = ttk.Frame(main_frame, padding=10)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        refresh_btn = ttk.Button(button_frame, text="刷新", command=self._load_records, width=8)
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        close_btn = ttk.Button(button_frame, text="关闭", command=self.window.destroy, width=8)
        close_btn.pack(side=tk.RIGHT, padx=10)
    
    def _create_records_list(self, parent):
        """创建记录列表
        
        Args:
            parent: 父容器
        """
        # 列表标题
        ttk.Label(parent, text="历史记录", font=("微软雅黑", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # 创建表格容器框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = [col["id"] for col in TABLE_COLUMNS]
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # 设置列标题和宽度
        for col in TABLE_COLUMNS:
            self.tree.heading(col["id"], text=col["text"])
            anchor = "center" if col["id"] == "id" else "w"
            self.tree.column(col["id"], width=col["width"]+40, anchor=anchor, minwidth=col["width"]+40)
        
        # 添加垂直滚动条
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview, style="Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=y_scrollbar.set)
        
        # 添加水平滚动条
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview, style="Vertical.TScrollbar")
        self.tree.configure(xscrollcommand=x_scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置表格容器的网格权重
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self._on_record_select)
        
        # 绑定双击事件（可选：双击行快速编辑）
        self.tree.bind("<Double-1>", self._on_row_double_click)
    
    def _create_details_view(self, parent):
        """创建详情视图
        
        Args:
            parent: 父容器
        """
        # 详情标题
        ttk.Label(parent, text="记录详情", font=("微软雅黑", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # 编辑区域
        edit_frame = ttk.Frame(parent)
        edit_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(edit_frame, text="项目/事务:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
        self.task_entry = ttk.Entry(edit_frame, width=40, font=("微软雅黑", 12))
        self.task_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # 保存按钮
        self.save_btn = ttk.Button(edit_frame, text="保存修改", command=self._save_changes)
        self.save_btn.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)
        self.save_btn.config(state="disabled")
        
        # 删除按钮
        self.delete_btn = ttk.Button(edit_frame, text="删除记录", command=self._delete_record)
        self.delete_btn.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)
        self.delete_btn.config(state="disabled")
        
        # 时间信息
        time_frame = ttk.Frame(parent)
        time_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(time_frame, text="创建时间:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
        self.created_label = ttk.Label(time_frame, text="", font=("微软雅黑", 12))
        self.created_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(time_frame, text="更新时间:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=(20, 0))
        self.updated_label = ttk.Label(time_frame, text="", font=("微软雅黑", 12))
        self.updated_label.pack(side=tk.LEFT, padx=10)
        
        # 图片预览
        preview_frame = ttk.LabelFrame(parent, text="截图预览", padding=20)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 增强预览区显示效果
        preview_container = ttk.Frame(preview_frame, padding=5)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # 为预览区设置更明显的边框
        self.preview_label = ttk.Label(
            preview_container, 
            borderwidth=2, 
            relief="groove", 
            anchor="center", 
            style="Preview.TLabel"
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 添加空预览提示
        self.empty_preview_text = "选择记录以查看截图"
        self.preview_label.config(text=self.empty_preview_text)
    
    def _on_record_select(self, event):
        """记录选择事件处理
        
        Args:
            event: 事件对象
        """
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # 获取选中项的ID
        item = selected_items[0]
        values = self.tree.item(item, 'values')
        record_id = int(values[0])
        
        # 获取记录详情
        record = data_manager.get_record_by_id(record_id)
        if not record:
            return
        
        self.selected_record = record
        
        # 更新界面
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, record.get('task_name', ''))
        
        # 格式化时间
        try:
            created_at = datetime.fromisoformat(record.get('created_at', '')).strftime('%Y-%m-%d %H:%M:%S')
            updated_at = datetime.fromisoformat(record.get('updated_at', '')).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            created_at = record.get('created_at', '')
            updated_at = record.get('updated_at', '')
        
        self.created_label.config(text=created_at)
        self.updated_label.config(text=updated_at)
        
        # 加载图片
        image_path = record.get('image_path', '')
        print(f"尝试加载图片: {image_path}")
        
        # 尝试不同的路径格式
        paths_to_try = [
            image_path,
            image_path.replace('/', '\\'),
            image_path.replace('\\', '/'),
            os.path.normpath(image_path),
            os.path.abspath(os.path.basename(image_path)),
            os.path.join(SCREENSHOT_DIR, os.path.basename(image_path))
        ]
        
        image_loaded = False
        for path in paths_to_try:
            if os.path.exists(path):
                print(f"找到可用路径: {path}")
                try:
                    # 加载图片
                    self.current_image = load_image_from_path(path)
                    if self.current_image:
                        # 获取预览区域的大小
                        preview_width = self.preview_label.winfo_width() - 30  # 考虑内边距
                        preview_height = self.preview_label.winfo_height() - 30
                        
                        # 如果尺寸太小，使用默认值
                        if preview_width < 100 or preview_height < 100:
                            preview_width = 600
                            preview_height = 400
                            
                        # 保持纵横比缩放图片
                        img_width, img_height = self.current_image.size
                        ratio = min(preview_width/img_width, preview_height/img_height)
                        new_width = int(img_width * ratio)
                        new_height = int(img_height * ratio)
                        
                        # 调整图片大小并创建预览
                        resized_img = self.current_image.resize((new_width, new_height), Image.LANCZOS)
                        self.image_preview = ImageTk.PhotoImage(resized_img)
                        
                        # 更新预览，清除文本
                        self.preview_label.config(image=self.image_preview, text="")
                        image_loaded = True
                        break
                except Exception as e:
                    print(f"加载图片失败: {e}")
        
        if not image_loaded:
            print(f"无法找到或加载图片: {image_path}")
            self.current_image = None
            self.image_preview = None
            self.preview_label.config(image="", text="图片加载失败")
        
        # 启用按钮
        self.save_btn.config(state="normal")
        self.delete_btn.config(state="normal")
    
    def _save_changes(self):
        """保存修改"""
        if not self.selected_record:
            return
        
        # 获取修改后的值
        new_task_name = self.task_entry.get().strip()
        if not new_task_name:
            messagebox.showerror("错误", "项目/事务名称不能为空")
            return
        
        # 更新记录
        success = data_manager.update_record(self.selected_record['id'], new_task_name)
        if success:
            messagebox.showinfo("成功", "记录已更新")
            self._load_records()  # 刷新列表
        else:
            messagebox.showerror("错误", "更新记录失败")
    
    def _delete_record(self):
        """删除记录"""
        if not self.selected_record:
            return
            
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除该记录吗？"):
            return
            
        # 删除记录
        success, image_path = data_manager.delete_record(self.selected_record['id'])
        if success:
            # 删除图片文件
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except OSError:
                    pass
                    
            messagebox.showinfo("成功", "记录已删除")
            self._load_records()  # 刷新列表
            self._clear_details()  # 清空详情
        else:
            messagebox.showerror("错误", "删除记录失败")
            
    def _clear_details(self):
        """清空详情区域"""
        self.selected_record = None
        self.task_entry.delete(0, tk.END)
        self.created_label.config(text="")
        self.updated_label.config(text="")
        self.preview_label.config(image="", text=self.empty_preview_text)
        self.current_image = None
        self.image_preview = None
        
        # 禁用按钮
        self.save_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")

    def _load_records(self):
        """加载记录列表"""
        # 清空现有记录
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取所有记录
        records = data_manager.get_all_records()
        
        # 按时间倒序排序
        records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # 添加到表格（设置交替行的tag）
        for i, record in enumerate(records):
            # 格式化时间
            timestamp = record.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                formatted_time = timestamp
            
            values = [
                record.get('id', ''),
                record.get('task_name', ''),
                formatted_time
            ]
            
            # 设置交替行的tag
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert('', tk.END, values=values, tags=(str(record.get('id')), tag))
        
        # 配置交替行的颜色
        if self.is_dark_mode:
            self.tree.tag_configure("even", background="#252540")
            self.tree.tag_configure("odd", background="#2a2a45")
        else:
            self.tree.tag_configure("even", background="#f9f9f9")
            self.tree.tag_configure("odd", background="#ffffff")

    def _filter_records(self):
        """筛选记录"""
        keyword = self.filter_entry.get().strip()
        date_from = self.filter_start.get().strip()
        date_to = self.filter_end.get().strip()
        records = data_manager.search_records(keyword, date_from, date_to)
        
        # 清空现有记录
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 按时间倒序排序
        records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # 添加到表格（设置交替行的tag）
        for i, record in enumerate(records):
            timestamp = record.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                formatted_time = timestamp
                
            values = [record.get('id', ''), record.get('task_name', ''), formatted_time]
            
            # 设置交替行的tag
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert('', tk.END, values=values, tags=(str(record.get('id')), tag))

    def _export_csv(self):
        import csv
        from tkinter import filedialog, messagebox
        # 获取当前表格内容
        items = self.tree.get_children()
        if not items:
            messagebox.showinfo("导出", "没有可导出的记录！")
            return
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")],
            title="导出为CSV"
        )
        if not file_path:
            return
        # 写入CSV
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([col["text"] for col in TABLE_COLUMNS])
            for item in items:
                row = self.tree.item(item, 'values')
                writer.writerow(row)
        messagebox.showinfo("导出", f"已导出到 {file_path}")

    def _on_row_double_click(self, event):
        """双击行事件处理，可以考虑添加快速编辑功能"""
        # 目前只实现与单击相同的功能，可以根据需要扩展
        self._on_record_select(event)

    def _update_theme(self, is_dark_mode=None):
        """更新界面主题
        
        Args:
            is_dark_mode: 是否深色模式，None表示使用父窗口的设置
        """
        if is_dark_mode is not None:
            self.is_dark_mode = is_dark_mode
        elif hasattr(self.parent, 'is_dark_mode'):
            self.is_dark_mode = self.parent.is_dark_mode
            
        # 获取新的主题颜色
        self.theme_colors = self.get_theme_colors()
        
        # 更新窗口背景色
        self.window.configure(bg=self.theme_colors["background"])
        
        # 重新设置样式
        self._setup_styles()
        
        # 更新交替行的颜色
        if self.is_dark_mode:
            self.tree.tag_configure("even", background="#252540")
            self.tree.tag_configure("odd", background="#2a2a45")
        else:
            self.tree.tag_configure("even", background="#f9f9f9")
            self.tree.tag_configure("odd", background="#ffffff")
        
        # 更新预览标签背景色
        if hasattr(self, 'preview_label'):
            if self.preview_label.cget("image") == "":
                # 如果没有图像，更新文本颜色
                self.preview_label.config(
                    background=self.theme_colors["preview_bg"],
                    foreground=self.theme_colors["secondary_text"],
                    text=self.empty_preview_text
                )