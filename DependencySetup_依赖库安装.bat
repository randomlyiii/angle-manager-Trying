@echo off
chcp 65001 >nul
echo ========================================
echo 自动化测试工具 - 依赖库安装脚本
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python环境
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo Python环境检测成功!
echo.

echo [2/3] 升级pip...
python -m pip install --upgrade pip
echo.

echo [3/3] 安装依赖库...
pip install -r requirements.txt
echo.

echo ========================================
echo 依赖库安装完成!
echo ========================================
echo.
echo 提示:
echo 1. 请将ADB工具放置在 externals/adb/ 目录下
echo 2. 请将识图模板放置在 resource/templates/ 目录下
echo 3. 运行 python Python/main.py 启动程序
echo.
pause
