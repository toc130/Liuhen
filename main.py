"""
留痕软件 - 主程序入口

这个程序用于记录工作活动，包括时间、事务和屏幕截图。
"""

import tkinter as tk
import sys
import os
import traceback
from PIL import Image

# 检测是否为PyInstaller打包环境
def is_pyinstaller():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# 获取正确的应用根目录
def get_app_root():
    if is_pyinstaller():
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

# 确保src目录在Python路径中
app_root = get_app_root()
sys.path.insert(0, app_root)
print(f"应用根目录: {app_root}")
print(f"Python路径: {sys.path}")

def main():
    """程序主入口"""
    try:
        print("开始加载模块...")
        
        # 导入必要的模块
        from src.config import ensure_dirs, APP_NAME, APP_VERSION
        print("成功导入config模块")
        
        # 导入配置管理器，预加载用户配置
        from src.utils.config_manager import default_config_manager
        print("加载用户配置完成")
        
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
        
        # 设置窗口图标 - 处理打包后路径
        icon_path = os.path.join(app_root, "assets", "icons", "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
            except Exception as e:
                print(f"设置图标失败: {e}")
        
        # 获取用户界面配置
        startup_maximized = default_config_manager.get_value("ui", "startup_maximized", True)
        
        # 适应不同的屏幕尺寸和分辨率
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        if startup_maximized and screen_width > 1366 and screen_height > 768:
            # 大屏幕且配置为最大化时，最大化窗口
            root.state('zoomed')
        else:
            # 较小屏幕或不需要最大化时，适当调整大小
            window_width = min(1024, screen_width - 100)
            window_height = min(768, screen_height - 100)
            root.geometry(f"{window_width}x{window_height}+{(screen_width-window_width)//2}+{(screen_height-window_height)//2}")
            
        print("Tkinter初始化完成")
        
        print("创建应用实例...")
        # 初始化应用
        app = ActivityTrackerApp(root)
        
        # 应用用户配置
        default_config_manager.apply_config(app)
        
        # 设置默认马赛克块大小
        app.mosaic_size = 40
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