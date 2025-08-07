"""
数据库模块单元测试
Database Module Unit Tests
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestDataValidation(unittest.TestCase):
    """数据验证测试 - 最重要的测试"""
    
    def test_data_file_existence(self):
        """测试数据文件是否存在"""
        english_file = os.path.join(project_root, "data", "main", "dataset_english.json")
        chinese_file = os.path.join(project_root, "data", "main", "dataset_chinese.json")
        training_file = os.path.join(project_root, "data", "training_data.json")
        
        self.assertTrue(os.path.exists(english_file), "英文数据文件不存在")
        self.assertTrue(os.path.exists(chinese_file), "中文数据文件不存在")
        self.assertTrue(os.path.exists(training_file), "训练数据文件不存在")
    
    def test_data_consistency(self):
        """测试数据一致性 - 关键测试"""
        english_file = os.path.join(project_root, "data", "main", "dataset_english.json")
        chinese_file = os.path.join(project_root, "data", "main", "dataset_chinese.json")
        
        with open(english_file, 'r', encoding='utf-8') as f:
            english_data = json.load(f)
        
        with open(chinese_file, 'r', encoding='utf-8') as f:
            chinese_data = json.load(f)
        
        # 检查记录数一致性
        self.assertEqual(len(english_data), len(chinese_data), "英文和中文数据记录数不一致")
        
        # 检查数据结构
        if chinese_data:
            sample = chinese_data[0]
            required_fields = ['Context', 'Response', 'original_Context', 'original_Response']
            for field in required_fields:
                self.assertIn(field, sample, f"缺少必需字段: {field}")
    
    def test_data_quality(self):
        """测试数据质量"""
        chinese_file = os.path.join(project_root, "data", "main", "dataset_chinese.json")
        
        with open(chinese_file, 'r', encoding='utf-8') as f:
            chinese_data = json.load(f)
        
        # 检查是否有空数据
        empty_count = 0
        for item in chinese_data[:10]:  # 只检查前10个样本
            if not item.get('Context') or not item.get('Response'):
                empty_count += 1
        
        self.assertLess(empty_count, 2, "存在过多空数据")


class TestConfigurationLoading(unittest.TestCase):
    """配置加载测试"""
    
    def test_config_file_exists(self):
        """测试配置文件是否存在"""
        config_file = os.path.join(project_root, "config", ".env")
        self.assertTrue(os.path.exists(config_file), "配置文件不存在")
    
    @patch.dict(os.environ, {
        'MONGODB_URI': 'mongodb://localhost:27017/',
        'DATABASE_NAME': 'test_db',
        'COLLECTION_NAME': 'test_collection'
    })
    def test_config_loading(self):
        """测试配置加载"""
        from dotenv import load_dotenv
        
        # 这个测试验证环境变量机制是否正常
        self.assertEqual(os.getenv('MONGODB_URI'), 'mongodb://localhost:27017/')
        self.assertEqual(os.getenv('DATABASE_NAME'), 'test_db')


class TestModuleImports(unittest.TestCase):
    """模块导入测试"""
    
    def test_database_modules_import(self):
        """测试数据库模块导入"""
        try:
            from src.database import DatabaseManager, DatabaseImporter, DatabaseVerifier
            self.assertTrue(True, "数据库模块导入成功")
        except ImportError as e:
            self.fail(f"数据库模块导入失败: {e}")
    
    def test_translation_module_import(self):
        """测试翻译模块导入"""
        try:
            from src.translation import DeepSeekTranslator
            self.assertTrue(True, "翻译模块导入成功")
        except ImportError as e:
            self.fail(f"翻译模块导入失败: {e}")


class TestBasicFunctionality(unittest.TestCase):
    """基础功能测试"""
    
    @patch('pymongo.MongoClient')
    def test_database_manager_init(self, mock_client):
        """测试数据库管理器初始化（模拟连接）"""
        # 模拟MongoDB连接
        mock_client.return_value.admin.command.return_value = True
        
        try:
            from src.database.database_manager import DatabaseManager
            
            # 使用环境变量模拟
            with patch.dict(os.environ, {
                'MONGODB_URI': 'mongodb://localhost:27017/',
                'DATABASE_NAME': 'test_db',
                'COLLECTION_NAME': 'test_collection'
            }):
                manager = DatabaseManager()
                self.assertIsNotNone(manager, "数据库管理器创建失败")
        except Exception as e:
            self.fail(f"数据库管理器初始化失败: {e}")
    
    def test_deepseek_translator_init(self):
        """测试DeepSeek翻译器初始化"""
        try:
            from src.translation.translate_with_deepseek import DeepSeekTranslator
            translator = DeepSeekTranslator("test-api-key")
            
            self.assertEqual(translator.api_key, "test-api-key")
            self.assertIn("deepseek.com", translator.base_url)
        except Exception as e:
            self.fail(f"翻译器初始化失败: {e}")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 