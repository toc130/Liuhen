"""
记录查询界面模块 - 实现记录的查询和编辑功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
from PIL import Image, ImageTk

from src.config import UI_FONT_BOLD, UI_FONT_NORMAL, TABLE_COLUMNS, SCREENSHOT_DIR
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
        self.window = tk.Toplevel(parent)
        self.window.title("查询记录")
        self.window.geometry("900x600")
        self.window.minsize(800, 500)
        self.window.state('zoomed')  # 启动时最大化
        # self.window.transient(parent)  # 注释掉或删除
        self.window.grab_set()           # 保持模态
        self.window.resizable(True, True)
        self.center_window(900, 600)
        self.window.configure(bg="#fafbfc")
        self._setup_styles()
        
        # 当前选中的记录
        self.selected_record = None
        self.current_image = None
        self.image_preview = None
        
        # 创建界面
        self._create_widgets()
        
        # 加载记录
        self._load_records()
    
    def _setup_styles(self):
        style = ttk.Style(self.window)
        style.theme_use('clam')
        style.configure("TFrame", background="#fafbfc")
        style.configure("TLabelframe", background="#fafbfc", font=("微软雅黑", 12, "bold"), padding=12)
        style.configure("TLabelframe.Label", background="#fafbfc", font=("微软雅黑", 12, "bold"))
        style.configure("TLabel", background="#fafbfc", font=("微软雅黑", 12))
        style.configure("TButton", font=("微软雅黑", 12), padding=8)
        style.configure("Treeview", font=("微软雅黑", 14), rowheight=40, fieldbackground="#fff", background="#fff")
        style.configure("Treeview.Heading", font=("微软雅黑", 14, "bold"), background="#f0f0f0")
        style.map("Treeview", background=[('selected', '#e6f7ff')], foreground=[('selected', '#222')])
    
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
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(filter_frame, text="关键词:").pack(side=tk.LEFT)
        self.filter_entry = ttk.Entry(filter_frame, width=20)
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text="开始日期:").pack(side=tk.LEFT, padx=(10, 0))
        self.filter_start = ttk.Entry(filter_frame, width=12)
        self.filter_start.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text="结束日期:").pack(side=tk.LEFT, padx=(10, 0))
        self.filter_end = ttk.Entry(filter_frame, width=12)
        self.filter_end.pack(side=tk.LEFT, padx=5)
        filter_btn = ttk.Button(filter_frame, text="筛选", command=self._filter_records)
        filter_btn.pack(side=tk.LEFT, padx=10)
        export_btn = ttk.Button(filter_frame, text="导出CSV", command=self._export_csv)
        export_btn.pack(side=tk.RIGHT, padx=10)
        # 主体区
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
        list_frame = ttk.Frame(paned_window, padding=10)
        paned_window.add(list_frame, weight=1)
        details_frame = ttk.Frame(paned_window, padding=10)
        paned_window.add(details_frame, weight=2)
        self._create_records_list(list_frame)
        sep = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=8)
        self._create_details_view(details_frame)
        button_frame = ttk.Frame(main_frame, padding=10)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        refresh_btn = ttk.Button(button_frame, text="刷新", command=self._load_records)
        refresh_btn.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)
        close_btn = ttk.Button(button_frame, text="关闭", command=self.window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=10, ipadx=10, ipady=5)
    
    def _create_records_list(self, parent):
        """创建记录列表
        
        Args:
            parent: 父容器
        """
        # 列表标题
        ttk.Label(parent, text="历史记录", font=("微软雅黑", 13, "bold"), background="#fafbfc").pack(anchor=tk.W, pady=(0, 10))
        
        # 创建表格
        columns = [col["id"] for col in TABLE_COLUMNS]
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        
        # 设置列标题和宽度
        for col in TABLE_COLUMNS:
            self.tree.heading(col["id"], text=col["text"])
            anchor = "center" if col["id"] == "id" else "w"
            self.tree.column(col["id"], width=col["width"]+40, anchor=anchor, minwidth=col["width"]+40)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self._on_record_select)
    
    def _create_details_view(self, parent):
        """创建详情视图
        
        Args:
            parent: 父容器
        """
        # 详情标题
        ttk.Label(parent, text="记录详情", font=("微软雅黑", 13, "bold"), background="#fafbfc").pack(anchor=tk.W, pady=(0, 10))
        
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
        preview_frame = ttk.LabelFrame(parent, text="截图预览", padding=20, style="TLabelframe")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_label = ttk.Label(preview_frame, borderwidth=2, relief="groove", anchor="center", background="#fff")
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def _load_records(self):
        """加载记录列表"""
        # 清空现有记录
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取所有记录
        records = data_manager.get_all_records()
        
        # 按时间倒序排序
        records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # 添加到表格
        for record in records:
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
            
            self.tree.insert('', tk.END, values=values, tags=(str(record.get('id')),))
    
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
                        preview_width = self.preview_label.winfo_width() or 400
                        preview_height = self.preview_label.winfo_height() or 300
                        
                        # 调整图片大小并创建预览
                        self.image_preview = ImageTk.PhotoImage(
                            self.current_image.resize(
                                (min(preview_width, self.current_image.width), 
                                min(preview_height, self.current_image.height)),
                                Image.LANCZOS
                            )
                        )
                        # 更新预览
                        self.preview_label.config(image=self.image_preview)
                        image_loaded = True
                        break
                except Exception as e:
                    print(f"加载图片失败: {e}")
        
        if not image_loaded:
            print(f"无法找到或加载图片: {image_path}")
            self.current_image = None
            self.image_preview = None
            self.preview_label.config(image="")
        
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
        self.preview_label.config(image="")
        self.current_image = None
        self.image_preview = None
        
        # 禁用按钮
        self.save_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")

    def _filter_records(self):
        keyword = self.filter_entry.get().strip()
        date_from = self.filter_start.get().strip()
        date_to = self.filter_end.get().strip()
        records = data_manager.search_records(keyword, date_from, date_to)
        # 清空现有记录
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 按时间倒序排序
        records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        for record in records:
            timestamp = record.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                formatted_time = timestamp
            values = [record.get('id', ''), record.get('task_name', ''), formatted_time]
            self.tree.insert('', tk.END, values=values, tags=(str(record.get('id')),))

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