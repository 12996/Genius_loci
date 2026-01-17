@echo off
REM 万物有灵项目环境配置脚本
REM 为conda things_soul环境配置依赖

echo ========================================
echo 万物有灵 - 环境配置
echo ========================================
echo.

REM 检查conda
where conda >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到conda，请先安装Anaconda或Miniconda
    pause
    exit /b 1
)

echo [1/5] 激活conda环境: things_soul
call conda activate things_soul
if errorlevel 1 (
    echo.
    echo [错误] 环境things_soul不存在
    echo.
    echo 创建环境命令:
    echo   conda create -n things_soul python=3.9 -y
    echo.
    pause
    exit /b 1
)

echo.
echo [2/5] 检查Python版本
python --version

echo.
echo [3/5] 升级httpx（解决依赖冲突）
echo 正在升级httpx到0.26.0+...
pip install "httpx>=0.26.0,<0.30.0" --force-reinstall

echo.
echo [4/5] 安装项目依赖
pip install -r requirements.txt

echo.
echo [5/5] 安装Supabase包
pip install supabase

echo.
echo ========================================
echo 配置完成！
echo ========================================
echo.
echo 下一步:
echo   1. 运行测试: python test_database.py
echo   2. 启动服务: python app.py
echo.
echo ========================================
pause
