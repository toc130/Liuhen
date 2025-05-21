@echo off
echo ===================================
echo       留痕软件打包脚本
echo ===================================
echo.

echo 正在创建虚拟环境...
python -m venv venv

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖包...
pip install -r requirements.txt

echo.
echo 开始打包...
python build.py

echo.
echo 打包完成后，请检查dist目录下的可执行文件。
echo.
echo 按任意键退出...
pause > nul 