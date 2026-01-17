@echo off
REM 万物有灵后端服务启动脚本 (Windows)

echo ========================================
echo 万物有灵后端服务 v2.0
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查依赖包...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo [提示] Flask未安装，正在安装依赖...
    pip install -r requirements.txt
) else (
    echo [OK] 依赖包已安装
)

echo.
echo [2/4] 检查配置文件...
if not exist .env (
    echo [提示] 创建.env配置文件...
    copy .env.example .env
    echo [警告] 请编辑.env文件配置MODELSCOPE_API_KEY（可选）
) else (
    echo [OK] 配置文件已存在
)

echo.
echo [3/4] 启动后端服务...
echo 服务地址: http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.

python app.py

pause
