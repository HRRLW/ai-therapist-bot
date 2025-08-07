# AI心理健康咨询机器人项目 Makefile
# AI Therapist Bot Project Makefile

# Python解释器路径
PYTHON = ./venv/bin/python

.PHONY: help install test clean run-import run-verify run-manage run-translate

# 默认目标
help:
	@echo "🤖 AI心理健康咨询机器人项目 - 可用命令："
	@echo ""
	@echo "环境管理 Environment Management:"
	@echo "  install     安装依赖包"
	@echo "  clean       清理临时文件"
	@echo ""
	@echo "数据库操作 Database Operations:"
	@echo "  run-import  导入数据到MongoDB"
	@echo "  run-verify  验证数据库状态"
	@echo "  run-manage  数据库管理"
	@echo ""
	@echo "数据处理 Data Processing:"
	@echo "  run-translate  翻译英文数据"
	@echo ""
	@echo "测试 Testing:"
	@echo "  test        运行测试"
	@echo ""

# 安装依赖
install:
	@echo "📦 安装项目依赖..."
	pip install -r requirements.txt
	@echo "✅ 依赖安装完成"

# 运行测试
test:
	@echo "🧪 运行测试..."
	$(PYTHON) -m unittest tests.unit.test_database -v
	@echo "✅ 测试完成"

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name "*.tmp" -delete
	@echo "✅ 清理完成"

# 数据库操作
run-import:
	@echo "🚀 启动数据导入..."
	$(PYTHON) run.py import

run-verify:
	@echo "🔍 启动数据验证..."
	$(PYTHON) run.py verify

run-manage:
	@echo "📊 启动数据库管理..."
	$(PYTHON) run.py manage

run-translate:
	@echo "🌐 启动数据翻译..."
	$(PYTHON) run.py translate

# 开发环境设置
dev-setup:
	@echo "🛠️ 设置开发环境..."
	python -m venv venv
	source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ 开发环境设置完成"

# 生成requirements.txt
freeze:
	@echo "📋 生成依赖文件..."
	$(PYTHON) -m pip freeze > requirements.txt
	@echo "✅ requirements.txt 已更新" 