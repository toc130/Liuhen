"""
留痕软件打包脚本
"""
import os
import sys
import subprocess
import shutil

# 项目名称
APP_NAME = "留痕软件"
# 主程序入口
MAIN_SCRIPT = "main.py"
# 图标路径
ICON_PATH = os.path.join("assets", "icons", "app_icon.ico")
# 需要包含的数据文件
ADDED_FILES = [
    ("assets", "assets"),
    ("data", "data"),
]

def clean_build():
    """清理上次构建产生的文件"""
    print("正在清理之前的构建文件...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    for item in os.listdir("."):
        if item.endswith(".spec"):
            os.remove(item)

def run_pyinstaller():
    """运行PyInstaller打包"""
    print("正在准备打包...")
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # 使用GUI模式，不显示控制台窗口
        "--onefile",   # 打包成单个exe文件
        "--clean",     # 清理临时文件
        "--noconfirm"  # 不显示确认对话框
    ]
    
    # 添加图标
    if os.path.exists(ICON_PATH):
        print(f"使用图标: {ICON_PATH}")
        cmd.extend(["--icon", ICON_PATH])
    else:
        print("警告: 未找到图标文件，将使用默认图标")
    
    # 添加数据文件
    for src, dest in ADDED_FILES:
        if os.path.exists(src):
            cmd.extend(["--add-data", f"{src};{dest}"])
    
    # 添加主脚本
    cmd.append(MAIN_SCRIPT)
    
    # 执行打包命令
    print("开始执行打包命令...")
    print(" ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        print("打包完成!")
        print(f"可执行文件位于: dist/{APP_NAME}.exe")
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False
    
    return True

def post_build():
    """打包后处理"""
    print("执行后处理操作...")
    
    # 确保程序正确处理相对路径
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        # 可以在这里添加对spec文件的修改，如有需要
        pass
    
    return True

if __name__ == "__main__":
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
        print(f"找到PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("错误: 未找到PyInstaller，请先安装: pip install pyinstaller")
        sys.exit(1)
    
    # 执行打包流程
    clean_build()
    if run_pyinstaller() and post_build():
        print("=======================================")
        print("打包成功! 可执行文件已生成。")
        print(f"文件路径: dist/{APP_NAME}.exe")
        print("=======================================")
    else:
        print("打包过程中出现错误，请查看上方日志。") 