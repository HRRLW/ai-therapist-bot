# 🤖 AI心理健康咨询机器人

**中文心理健康咨询对话数据库和AI训练系统**  
**Chinese Mental Health Counseling Database and AI Training System**

## 📋 项目简介 (Project Overview)

本项目致力于构建高质量的中文心理健康咨询对话数据库，为AI心理健康咨询系统的训练提供数据支持。项目采用精简的模块化架构，包含完整的数据翻译、处理、存储和管理流程。

This project is dedicated to building a high-quality Chinese mental health counseling dialogue database to provide data support for AI mental health counseling system training. The project adopts a streamlined modular architecture with complete data translation, processing, storage and management workflows.

## 🏗️ 项目架构 (Project Architecture)

```
ai-therapist-bot/
├── 📁 src/                    # 源代码模块 (44KB)
│   ├── 📁 database/          # 数据库操作模块
│   │   ├── import_to_mongodb.py      # 数据导入 (3.2KB)
│   │   ├── database_manager.py       # 数据库管理 (5.6KB)
│   │   └── verify_database.py        # 数据验证 (5.2KB)
│   ├── 📁 translation/       # 翻译模块
│   │   └── translate_with_deepseek.py # DeepSeek翻译 (6.6KB)
│   └── 📁 utils/            # 工具模块 (预留扩展)
├── 📁 config/               # 配置文件 (4KB)
│   └── .env                         # 环境变量
├── 📁 data/                 # 数据文件 (63MB)
│   ├── 📁 main/            # 主要数据 (14MB)
│   │   ├── dataset_english.json    # 英文数据 (4.6MB)
│   │   └── dataset_chinese.json    # 中文数据 (8.5MB)
│   ├── 📁 backups/         # 精简备份 (40MB, 5个文件)
│   └── training_data.json          # 训练数据 (9MB)
├── 📁 tests/                # 测试代码 (8KB)
│   └── 📁 unit/            # 单元测试
│       └── test_database.py         # 数据库模块测试 (9个测试)
├── 📁 logs/                 # 日志文件
├── run.py                   # 主启动脚本 (4KB)
├── setup.py                 # 项目安装配置 (4KB)
├── requirements.txt         # 精简依赖 (4KB)
├── Makefile                 # 项目管理命令 (4KB)
└── README.md               # 项目说明 (本文件)
```

## 🚀 快速开始 (Quick Start)

### 1. 环境准备 (Environment Setup)

```bash
# 克隆项目
git clone <repository-url>
cd ai-therapist-bot

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
make install
# 或 pip install -r requirements.txt
```

### 2. 配置环境变量 (Configure Environment)

编辑 `config/.env` 文件：

```env
# MongoDB配置
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=mental_health_counseling
COLLECTION_NAME=conversations

# DeepSeek API配置 (用于翻译)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. 一键操作 (One-Click Operations)

```bash
# 验证数据库状态
python run.py verify

# 数据库管理
python run.py manage

# 导入数据 (如需要)
python run.py import

# 翻译数据 (如需要)
python run.py translate
```

## 📊 数据统计 (Data Statistics)

- **原始数据**: 3,512条英文心理健康咨询对话 (4.6MB)
- **翻译数据**: 3,512条中文心理健康咨询对话 (8.5MB)
- **训练数据**: 优化格式的训练数据 (9.0MB)
- **数据格式**: Context (问题) + Response (回答)
- **翻译质量**: DeepSeek API专业翻译
- **数据完整率**: 100%

## 🎯 核心功能 (Core Features)

### 🌐 数据翻译
- DeepSeek API高质量翻译
- 进度保存和断点续传
- 错误处理和重试机制

### 💾 数据库管理
- MongoDB存储和索引
- 数据验证和质量检查
- 灵活的查询接口
- 训练数据导出

### 🔍 数据验证
- 数据完整性检查
- 索引状态验证
- 搜索功能测试

### 🛠️ 开发工具
- 精简的模块化架构
- 标准化测试框架
- 便捷的命令行工具
- 自动化Makefile

## 📚 可用命令 (Available Commands)

| 命令 | 功能 | Makefile快捷方式 |
|------|------|------------------|
| `python run.py import` | 导入数据到MongoDB | `make run-import` |
| `python run.py verify` | 验证数据库状态 | `make run-verify` |
| `python run.py manage` | 数据库管理操作 | `make run-manage` |
| `python run.py translate` | 翻译英文数据 | `make run-translate` |

**开发命令:**

```bash
make install     # 安装依赖
make test        # 运行测试  
make clean       # 清理临时文件
make help        # 显示帮助
```

## 🧪 测试 (Testing)

### 🎯 测试覆盖范围 (Test Coverage)

本项目包含完整的单元测试套件，覆盖核心功能的关键风险点：

| 测试类别 | 测试内容 | 重要性 | 测试数量 |
|----------|----------|--------|----------|
| **数据验证测试** | 文件存在性、数据一致性、质量检查 | ⭐⭐⭐⭐⭐ | 3个测试 |
| **配置加载测试** | 配置文件、环境变量机制 | ⭐⭐⭐⭐ | 2个测试 |
| **模块导入测试** | 数据库模块、翻译模块导入 | ⭐⭐⭐⭐ | 2个测试 |
| **基础功能测试** | 数据库管理器、翻译器初始化 | ⭐⭐⭐ | 2个测试 |

### 🚀 运行测试 (Running Tests)

```bash
# 运行所有测试 (推荐)
make test

# 直接运行测试
./venv/bin/python -m unittest tests.unit.test_database -v

# 验证系统状态
python run.py verify
```

### ✅ 测试特点 (Test Features)

- **快速执行**: 所有测试在0.5秒内完成
- **无外部依赖**: 使用Mock避免实际数据库/API连接
- **数据安全**: 测试不会修改或删除实际数据
- **自动化**: 集成到Makefile中，一键运行
- **详细输出**: 提供详细的测试结果和错误信息

### 🔍 测试示例输出 (Test Output Example)

```
🧪 运行测试...
test_data_consistency ... ok          # 数据一致性验证
test_data_file_existence ... ok       # 数据文件存在性检查
test_data_quality ... ok              # 数据质量验证
test_config_file_exists ... ok        # 配置文件检查
test_config_loading ... ok            # 环境变量加载
test_database_modules_import ... ok   # 数据库模块导入
test_translation_module_import ... ok # 翻译模块导入
test_database_manager_init ... ok     # 数据库管理器初始化
test_deepseek_translator_init ... ok  # 翻译器初始化

Ran 9 tests in 0.542s - OK ✅
```

### 🎯 测试策略 (Testing Strategy)

我们采用**实用主义测试方法**：

- ✅ **重点测试**: 数据完整性和核心功能
- ✅ **快速反馈**: 秒级测试执行时间  
- ✅ **简单维护**: 单文件测试，标准库实现
- ❌ **避免过度**: 不测试外部API和复杂集成
- ❌ **避免依赖**: 不需要实际数据库连接 

## 📂 数据集说明 (Dataset Description)

本项目包含 **Depression User Reports Dataset**，该数据集来源于 Reddit，已进行匿名化处理，删除了用户ID和发布时间等个人信息。

### 数据文件信息
- **文件名称**: dataset.csv
- **文件大小**: ~13 MB
- **格式**: CSV
- **列数**: 3 列

### 字段说明
1. **title**  
   用户报告的简要标题或摘要。
2. **content**  
   用户的详细报告文本，包括个人经历、想法、感受以及与抑郁相关的描述。
3. **score**  
   Reddit 社区对该报告的评分或点赞数，可能反映了帖子的互动程度或认可度。

### 适用场景
- 文本分析与自然语言处理 (NLP)
- 情感分析与情绪识别
- 主题建模与聚类分析
- 抑郁症相关研究与内容分析
- 机器学习模型训练与评估

### 使用注意事项
- 内容可能涉及敏感的心理健康信息，使用时需遵守伦理规范。
- 数据已匿名化，但如与其他数据结合使用，应注意隐私保护。
- 本数据集遵循 **CC0: Public Domain Dedication** 协议，可自由使用。