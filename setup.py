#!/usr/bin/env python3
"""
AI心理健康咨询机器人项目安装配置
AI Therapist Bot Project Setup Configuration
"""

from setuptools import setup, find_packages
import os

# 读取README
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# 读取requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ai-therapist-bot",
    version="1.0.0",
    description="中文心理健康咨询对话数据库和AI训练系统",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="AI Therapist Bot Team",
    author_email="team@ai-therapist-bot.com",
    url="https://github.com/ai-therapist-bot/ai-therapist-bot",
    
    # 包配置
    packages=find_packages(),
    include_package_data=True,
    
    # 依赖
    install_requires=read_requirements(),
    
    # Python版本要求
    python_requires=">=3.9",
    
    # 项目分类
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database :: Database Engines/Servers",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
    ],
    
    # 关键词
    keywords="ai, mental-health, chinese, mongodb, translation, deepseek",
    
    # 入口点
    entry_points={
        'console_scripts': [
            'ai-therapist=run:main',
        ],
    },
    
    # 项目URL
    project_urls={
        'Bug Reports': 'https://github.com/ai-therapist-bot/ai-therapist-bot/issues',
        'Source': 'https://github.com/ai-therapist-bot/ai-therapist-bot',
        'Documentation': 'https://github.com/ai-therapist-bot/ai-therapist-bot/docs',
    },
) 