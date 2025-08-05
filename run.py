#!/usr/bin/env python3
"""
AI心理健康咨询机器人 - 主启动脚本
AI Therapist Bot - Main Launch Script

用法 Usage:
  python run.py import     # 导入数据到MongoDB
  python run.py verify     # 验证数据库
  python run.py manage     # 数据库管理
  python run.py translate  # 翻译数据
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.database import DatabaseImporter, DatabaseManager, DatabaseVerifier


def print_usage():
    """打印使用说明"""
    print("🤖 AI心理健康咨询机器人 - 主启动脚本")
    print("=" * 50)
    print("用法:")
    print("  python run.py import     # 导入数据到MongoDB")
    print("  python run.py verify     # 验证数据库状态") 
    print("  python run.py manage     # 数据库管理")
    print("  python run.py translate  # 翻译英文数据")
    print("=" * 50)


def run_import():
    """运行数据导入"""
    print("🚀 启动数据导入...")
    from src.database.import_to_mongodb import main
    main()


def run_verify():
    """运行数据验证"""
    print("🔍 启动数据验证...")
    from src.database.verify_database import main
    main()


def run_manage():
    """运行数据库管理"""
    print("📊 启动数据库管理...")
    from src.database.database_manager import main
    main()


def run_translate():
    """运行数据翻译"""
    print("🌐 启动数据翻译...")
    from src.translation.translate_with_deepseek import main
    main()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'import':
        run_import()
    elif command == 'verify':
        run_verify()
    elif command == 'manage':
        run_manage()
    elif command == 'translate':
        run_translate()
    elif command in ['-h', '--help', 'help']:
        print_usage()
    else:
        print(f"❌ 未知命令: {command}")
        print_usage()


if __name__ == "__main__":
    main() 