#!/bin/bash
# 股票学习笔记本启动脚本

echo "=========================================="
echo "  股票学习笔记本"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[1/3] 检查依赖..."
python3 -c "import baostock" 2>/dev/null || pip3 install baostock -q
python3 -c "import flask" 2>/dev/null || pip3 install flask -q

echo ""
echo "[2/3] 初始化数据库..."
python3 models.py

echo ""
echo "[3/3] 启动服务..."
echo "  - 笔记本: http://localhost:5556"
echo "  - K线查看: http://localhost:5556/stock/600487"
echo ""

python3 app.py
