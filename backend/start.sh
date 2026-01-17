#!/bin/bash
# 万物有灵后端服务启动脚本 (Linux/Mac)

echo "========================================"
echo "万物有灵后端服务 v2.0"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python，请先安装Python 3.8+"
    exit 1
fi

echo "[1/4] 检查依赖包..."
if ! python3 -c "import Flask" &> /dev/null; then
    echo "[提示] Flask未安装，正在安装依赖..."
    pip3 install -r requirements.txt
else
    echo "[OK] 依赖包已安装"
fi

echo ""
echo "[2/4] 检查配置文件..."
if [ ! -f .env ]; then
    echo "[提示] 创建.env配置文件..."
    cp .env.example .env
    echo "[警告] 请编辑.env文件配置MODELSCOPE_API_KEY（可选）"
else
    echo "[OK] 配置文件已存在"
fi

echo ""
echo "[3/4] 启动后端服务..."
echo "服务地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py
