@echo off
echo ============================================================
echo 启动万物有灵 FastAPI 服务
echo ============================================================
echo.

cd /d "%~dp0"

echo 检查环境...
python --version
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

echo.
echo 启动服务...
echo 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ============================================================
echo.

python main.py

pause
