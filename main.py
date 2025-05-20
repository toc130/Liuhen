"""
留痕软件 - 主程序入口

这个程序用于记录工作活动，包括时间、事务和屏幕截图。
"""

import tkinter as tk
import sys
import os
import traceback
from PIL import Image

# 确保src目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print(f"Python路径: {sys.path}")

def main():
    """程序主入口"""
    try:
        print("开始加载模块...")
        
        # 导入必要的模块
        from src.config import ensure_dirs, APP_NAME, APP_VERSION
        print("成功导入config模块")
        
        from src.gui.app import ActivityTrackerApp
        print("成功导入app模块")
        
        print("创建必要的目录...")
        # 确保必要的目录存在
        ensure_dirs()
        print("目录创建完成")
        
        print("初始化Tkinter...")
        # 创建Tkinter根窗口
        root = tk.Tk()
        
        # 设置窗口图标和标题
        root.title(f"{APP_NAME} v{APP_VERSION}")
        root.state('zoomed')  # 启动时最大化
        print("Tkinter初始化完成")
        
        print("创建应用实例...")
        # 初始化应用
        app = ActivityTrackerApp(root)
        app.mosaic_size = 40  # 马赛克块大小，默认40
        print("应用实例创建完成")
        
        print("启动主循环...")
        # 启动主循环
        root.mainloop()
    except ImportError as e:
        error_message = f"导入模块错误: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        try:
            from tkinter import messagebox
            messagebox.showerror("模块导入错误", error_message)
        except:
            pass
    except Exception as e:
        error_message = f"程序启动错误: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        try:
            from tkinter import messagebox
            messagebox.showerror("启动错误", error_message)
        except:
            pass


if __name__ == "__main__":
    try:
        print("=== 留痕软件启动 ===")
        main()
    except Exception as e:
        print(f"未捕获的异常: {str(e)}")
        # print(traceback.format_exc())