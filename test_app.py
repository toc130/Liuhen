"""
留痕软件 - 简化测试版本
"""

import os
import sys
import tkinter as tk
import traceback

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui():
    """测试GUI是否能正常创建和显示"""
    try:
        print("初始化tkinter...")
        root = tk.Tk()
        root.title("测试窗口")
        root.geometry("400x300")
        
        # 添加一个简单的标签
        label = tk.Label(root, text="如果你能看到这个窗口，说明GUI可以正常工作")
        label.pack(pady=20)
        
        # 添加一个按钮
        button = tk.Button(root, text="关闭", command=root.destroy)
        button.pack(pady=10)
        
        print("启动GUI主循环...")
        root.mainloop()
        return True
    except Exception as e:
        print(f"GUI测试失败: {e}")
        traceback.print_exc()
        return False

def test_modules():
    """测试模块导入是否正常"""
    try:
        print("测试导入src.config...")
        from src.config import ensure_dirs, APP_NAME
        print(f"成功导入config，APP_NAME={APP_NAME}")
        
        print("测试导入src.utils.data_manager...")
        from src.utils.data_manager import DataManager
        print("成功导入DataManager")
        
        print("测试创建DataManager实例...")
        dm = DataManager()
        print("成功创建DataManager实例")
        
        print("测试导入src.utils.screenshot...")
        from src.utils.screenshot import load_image_from_path
        print("成功导入screenshot模块")
        
        return True
    except Exception as e:
        print(f"模块测试失败: {e}")
        traceback.print_exc()
        return False

def test_directories():
    """测试目录结构是否正确"""
    try:
        print("测试ensure_dirs...")
        from src.config import ensure_dirs
        ensure_dirs()
        
        # 检查目录是否存在
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        screenshots_dir = os.path.join(data_dir, "screenshots")
        
        print(f"检查data目录: {data_dir}, 存在: {os.path.exists(data_dir)}")
        print(f"检查screenshots目录: {screenshots_dir}, 存在: {os.path.exists(screenshots_dir)}")
        
        return os.path.exists(data_dir) and os.path.exists(screenshots_dir)
    except Exception as e:
        print(f"目录测试失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 开始测试程序 ===")
    
    print("\n=== 测试目录结构 ===")
    dirs_ok = test_directories()
    
    print("\n=== 测试模块导入 ===")
    modules_ok = test_modules()
    
    print("\n=== 测试GUI功能 ===")
    gui_ok = test_gui()
    
    print("\n=== 测试结果汇总 ===")
    print(f"目录结构: {'通过' if dirs_ok else '失败'}")
    print(f"模块导入: {'通过' if modules_ok else '失败'}")
    print(f"GUI功能: {'通过' if gui_ok else '失败'}")
    
    if dirs_ok and modules_ok and gui_ok:
        print("\n所有测试通过！应该可以正常启动主程序了。")
    else:
        print("\n有测试项目失败，请查看上面的错误信息。") 