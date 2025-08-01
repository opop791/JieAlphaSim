@echo off
setlocal enabledelayedexpansion

REM === 配置路径 ===
set PYTHON_PATH=H:\Python\python.exe
set PROJECT_DIR=D:\JieAlphaSim
set SCRIPT_NAME=JieAlphaSimPro_Integrated.py
set LOG_FILE=streamlit_launch.log
set PORT=8501
set PIP_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple

REM === 切换目录 ===
echo [🚀] 切换至项目目录: %PROJECT_DIR%
cd /d "%PROJECT_DIR%"

REM === 验证 Python 路径 ===
echo [🔍] 检查 Python 路径: !PYTHON_PATH!
if not exist "!PYTHON_PATH!" (
    echo [❌] Python 路径无效: !PYTHON_PATH!
    pause
    exit /b
)

REM === 验证 Python 脚本是否存在 ===
if not exist "!SCRIPT_NAME!" (
    echo [❌] 未找到脚本文件: !SCRIPT_NAME!
    echo 请确保该文件存在于: %PROJECT_DIR%
    pause
    exit /b
)

REM === 安装/修复依赖（使用清华镜像） ===
echo [📦] 安装依赖（使用清华源）...
"!PYTHON_PATH!" -m pip install --upgrade pip -i %PIP_MIRROR%
"!PYTHON_PATH!" -m pip install streamlit pandas numpy requests yfinance mplfinance plotly streamlit-autorefresh -i %PIP_MIRROR%

REM === 检查端口占用情况 ===
echo [🔍] 检查端口 %PORT% 是否占用...
netstat -aon | findstr :%PORT% >nul
if !errorlevel! EQU 0 (
    echo [⚠️] 端口 %PORT% 已被占用，自动切换到 8510...
    set PORT=8510
)

REM === 启动 Streamlit 应用 ===
echo [🌐] 启动应用中，请稍候...
start http://localhost:%PORT%
"!PYTHON_PATH!" -m streamlit run "!SCRIPT_NAME!" --server.port %PORT% >"%LOG_FILE%" 2>&1

echo.
echo [✅] 启动完成，日志已写入: %LOG_FILE%
echo 打开浏览器访问: http://localhost:%PORT%
echo.
echo 按任意键关闭窗口...
pause >nul
