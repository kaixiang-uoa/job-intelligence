#!/bin/bash

# Job Intelligence Scraper API 启动脚本

echo "🚀 Starting Job Intelligence Scraper API..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
fi

# 启动服务
echo "✅ Starting server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
