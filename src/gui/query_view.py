"""
查询界面模块 - 实现记录查询和编辑功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
from PIL import Image, ImageTk

from src.config import UI_FONT_BOLD, UI_FONT_NORMAL, TIME_FORMAT, SCREENSHOT_DIR
from src.utils.data_manager import DataManager
from src.utils.screenshot import load_image_from_path, resize_image_for_preview


class QueryView(ttk.Frame):
    """查询视图类，用于查询和编辑记录"""
    
    def __init__(self, parent):
        super().__init__(parent, padding="10")
        self.parent = parent
        
        # 创建数据管理器
        self.data_manager = DataManager()
        
        # 当前选中的记录
        self.selected_record = None
        self.current_image = None
        self.image_preview = None
        
        # 创建UI组件
        self._create_widgets()
        
        # 加载记录
        self.load_records()
    
    def _create_widgets(self):
        """创建UI组件"""
        # 创建搜索框架
        self._create_search_frame()
        
        # 创建记录列表框架
        self._create_records_frame()
        
        # 创建详情框架
        self._create_details_frame()
    
    def _create_search_frame(self):
        """创建搜索框架"""
        search_frame = ttk.LabelFrame(self, text="搜索条件", padding="5")
        search_frame.pack(fill=tk.X, pady=5)
        
        # 关键词搜索
        ttk.Label(search_frame, text="关键词:", font=UI_FONT_BOLD).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.keyword_entry = ttk.Entry(search_frame, width=20, font=UI_FONT_NORMAL)
        self.keyword_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 日期范围
        ttk.Label(search_frame, text="开始日期:", font=UI_FONT_BOLD).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.start_date_entry = ttk.Entry(search_frame, width=10, font=UI_FONT_NORMAL)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(search_frame, text="结束日期:", font=UI_FONT_BOLD).grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.end_date_entry = ttk.Entry(search_frame, width=10, font=UI_FONT_NORMAL)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # 搜索按钮
        self.search_btn = ttk.Button(search_frame, text="搜索", command=self.search_records)
        self.search_btn.grid(row=0, column=6, padx=5, pady=5)
        
        # 重置按钮
        self.reset_btn = ttk.Button(search_frame, text="重置", command=self.reset_search)
        self.reset_btn.grid(row=0, column=7, padx=5, pady=5)
    
    def _create_records_frame(self):
        """创建记录列表框架"""
        records_frame = ttk.LabelFrame(self, text="记录列表", padding="5")
        records_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建Treeview
        columns = ("id", "timestamp", "task_name")
        self.records_tree = ttk.Treeview(records_frame, columns=columns, show="headings")
        
        # 设置列标题
        self.records_tree.heading("id", text="ID")
        self.records_tree.heading("timestamp", text="时间")
        self.records_tree.heading("task_name", text="项目/事务")
        
        # 设置列宽
        self.records_tree.column("id", width=100)
        self.records_tree.column("timestamp", width=150)
        self.records_tree.column("task_name", width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(records_frame, orient=tk.VERTICAL, command=self.records_tree.yview)
        self.records_tree.configure(yscroll=scrollbar.set)
        
        # 布局
        self.records_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.records_tree.bind("<<TreeviewSelect>>", self.on_record_select)
    
    def _create_details_frame(self):
        """创建详情框架"""
        details_frame = ttk.LabelFrame(self, text="记录详情", padding="5")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左侧信息区域
        info_frame = ttk.Frame(details_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # 项目/事务
        ttk.Label(info_frame, text="项目/事务:", font=UI_FONT_BOLD).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.task_entry = ttk.Entry(info_frame, width=30, font=UI_FONT_NORMAL)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 时间
        ttk.Label(info_frame, text="时间:", font=UI_FONT_BOLD).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.time_label = ttk.Label(info_frame, text="", font=UI_FONT_NORMAL)
        self.time_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 附加说明
        ttk.Label(info_frame, text="附加说明:", font=UI_FONT_BOLD).grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        self.notes_text = tk.Text(info_frame, width=30, height=5, font=UI_FONT_NORMAL)
        self.notes_text.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 按钮区域
        button_frame = ttk.Frame(info_frame)
        button_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        self.save_btn = ttk.Button(button_frame, text="保存修改", command=self.save_changes)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(button_frame, text="删除记录", command=self.delete_record)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 右侧预览区域
        preview_frame = ttk.LabelFrame(details_frame, text="截图预览")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 初始状态下禁用按钮
        self.save_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
    
    def load_records(self):
        """加载所有记录"""
        # 清空现有记录
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        # 获取所有记录
        records = self.data_manager.get_all_records()
        
        # 添加到Treeview
        for record in records:
            # 格式化时间
            timestamp = record.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                formatted_time = timestamp
                
            self.records_tree.insert("", tk.END, values=(
                record.get('id', ''), 
                formatted_time, 
                record.get('task_name', '')
            ))
    
    def search_records(self):
        """搜索记录"""
        keyword = self.keyword_entry.get().strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        
        # 清空现有记录
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        # 搜索记录
        records = self.data_manager.search_records(keyword, start_date, end_date)
        
        # 添加到Treeview
        for record in records:
            # 格式化时间
            timestamp = record.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                formatted_time = timestamp
                
            self.records_tree.insert("", tk.END, values=(
                record.get('id', ''), 
                formatted_time, 
                record.get('task_name', '')
            ))
    
    def reset_search(self):
        """重置搜索条件"""
        self.keyword_entry.delete(0, tk.END)
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self.load_records()
    
    def on_record_select(self, event):
        """记录选择事件处理"""
        # 获取选中的项
        selection = self.records_tree.selection()
        if not selection:
            return
        
        # 获取记录ID
        item = self.records_tree.item(selection[0])
        record_id = int(item["values"][0])
        
        # 获取记录详情
        record = self.data_manager.get_record_by_id(record_id)
        if not record:
            return
        
        # 保存当前选中的记录
        self.selected_record = record
        
        # 更新详情区域
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, record.get('task_name', ''))
        
        # 格式化时间
        timestamp = record.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            formatted_time = timestamp
        
        self.time_label.config(text=formatted_time)
        
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, record.get('notes', ''))
        
        # 加载并显示图像
        image_path = record.get('image_path', '')
        print(f"尝试加载图片: {image_path}")
        
        # 尝试不同的路径格式
        paths_to_try = [
            image_path,
            image_path.replace('/', '\\'),
            image_path.replace('\\', '/'),
            os.path.normpath(image_path),
            os.path.basename(image_path),
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
                        preview_width = self.preview_label.winfo_width() or 300
                        preview_height = self.preview_label.winfo_height() or 200
            
            # 确保尺寸至少为1像素
            preview_width = max(1, preview_width)
            preview_height = max(1, preview_height)
            
            # 调整图像并显示
                        self.image_preview = ImageTk.PhotoImage(
                            self.current_image.resize(
                                (min(preview_width, self.current_image.width), 
                                min(preview_height, self.current_image.height)),
                                Image.LANCZOS
                            )
                        )
            self.preview_label.config(image=self.image_preview)
                        image_loaded = True
                        break
                except Exception as e:
                    print(f"加载图片失败: {e}")
        
        if not image_loaded:
            print(f"无法找到或加载图片: {image_path}")
            self.preview_label.config(image="")
        
        # 启用按钮
        self.save_btn.config(state="normal")
        self.delete_btn.config(state="normal")
    
    def save_changes(self):
        """保存修改"""
        if not self.selected_record:
            return
        
        # 获取修改后的值
        task_name = self.task_entry.get().strip()
        notes = self.notes_text.get(1.0, tk.END).strip()
        
        if not task_name:
            messagebox.showerror("错误", "项目/事务名称不能为空")
            return
        
        # 更新记录
        success = self.data_manager.update_record(
            self.selected_record.get('id'), task_name, notes)
        
        if success:
            messagebox.showinfo("成功", "记录已更新")
            # 刷新记录列表
            self.load_records()
        else:
            messagebox.showerror("错误", "更新记录失败")
    
    def delete_record(self):
        """删除记录"""
        if not self.selected_record:
            return
        
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除这条记录吗？这将同时删除截图文件。"):
            return
        
        # 删除记录
        success, image_path = self.data_manager.delete_record(self.selected_record.get('id'))
        
        if success:
            # 删除图片文件
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except OSError:
                    pass
                    
            messagebox.showinfo("成功", "记录已删除")
            # 清空详情区域
            self.task_entry.delete(0, tk.END)
            self.time_label.config(text="")
            self.notes_text.delete(1.0, tk.END)
            self.preview_label.config(image="")
            self.selected_record = None
            self.current_image = None
            self.image_preview = None
            
            # 禁用按钮
            self.save_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            
            # 刷新记录列表
            self.load_records()
        else:
            messagebox.showerror("错误", "删除记录失败: " + image_path)