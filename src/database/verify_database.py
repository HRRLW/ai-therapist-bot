"""
数据库验证脚本 - 验证MongoDB数据完整性
功能：数据统计 -> 质量检查 -> 索引验证 -> 搜索测试
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# 加载配置文件
config_path = os.path.join(project_root, 'config', '.env')
load_dotenv(config_path)

class DatabaseVerifier:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME')]
        self.collection = self.db[os.getenv('COLLECTION_NAME')]
        print("✅ MongoDB连接成功")
    
    def check_data_quality(self):
        """检查数据质量"""
        total = self.collection.count_documents({})
        chinese = self.collection.count_documents({'Context': {'$ne': ''}})
        english = self.collection.count_documents({'original_Context': {'$ne': ''}})
        
        print("📊 数据质量检查:")
        print(f"   总记录数: {total}")
        print(f"   中文记录数: {chinese}")
        print(f"   英文记录数: {english}")
        print(f"   数据完整率: {(chinese/total*100):.1f}%" if total > 0 else "   数据完整率: 0%")
        
        # 检查数据一致性
        if total == chinese == english:
            print("✅ 数据一致性检查通过")
            return True
        else:
            print("⚠️  数据一致性检查失败")
            return False
    
    def check_indexes(self):
        """检查索引状态"""
        indexes = list(self.collection.list_indexes())
        print(f"🔧 索引检查:")
        print(f"   索引数量: {len(indexes)}")
        
        for idx in indexes:
            name = idx.get('name', 'unnamed')
            key = idx.get('key', {})
            print(f"   - {name}: {dict(key)}")
        
        # 检查必要索引
        index_names = [idx['name'] for idx in indexes]
        required_indexes = ['_id_', 'translation_index', 'imported_at']
        
        missing = [idx for idx in required_indexes if idx not in index_names]
        if missing:
            print(f"⚠️  缺少索引: {missing}")
            return False
        else:
            print("✅ 索引检查通过")
            return True
    
    def test_search(self):
        """测试搜索功能"""
        print("🔍 搜索功能测试:")
        
        try:
            # 测试正则搜索
            chinese_results = self.collection.find({
                'Context': {'$regex': '抑郁', '$options': 'i'}
            }).limit(3)
            chinese_count = len(list(chinese_results))
            
            english_results = self.collection.find({
                'original_Context': {'$regex': 'depression', '$options': 'i'}
            }).limit(3)
            english_count = len(list(english_results))
            
            print(f"   中文关键词搜索: {chinese_count} 条")
            print(f"   英文关键词搜索: {english_count} 条")
            
            # 测试索引查询
            index_result = self.collection.find_one({'translation_index': 1})
            if index_result:
                print("   索引查询: 正常")
            else:
                print("   索引查询: 异常")
            
            print("✅ 搜索功能正常")
            return True
            
        except Exception as e:
            print(f"❌ 搜索功能异常: {e}")
            return False
    
    def show_sample(self):
        """显示样本数据"""
        sample = self.collection.find_one({})
        if sample:
            print("📄 样本数据:")
            print(f"   记录ID: {sample.get('_id')}")
            print(f"   翻译索引: {sample.get('translation_index')}")
            print(f"   导入时间: {sample.get('imported_at')}")
            print(f"   中文问题: {sample.get('Context', '')[:60]}...")
            print(f"   中文回答: {sample.get('Response', '')[:60]}...")
        else:
            print("❌ 无法获取样本数据")
    
    def run_full_verification(self):
        """运行完整验证"""
        print("🔬 开始数据库验证")
        print("=" * 40)
        
        # 数据质量检查
        data_ok = self.check_data_quality()
        print()
        
        # 索引检查
        index_ok = self.check_indexes()
        print()
        
        # 搜索测试
        search_ok = self.test_search()
        print()
        
        # 显示样本
        self.show_sample()
        print()
        
        # 总结
        print("=" * 40)
        if data_ok and index_ok and search_ok:
            print("🎉 数据库验证通过！")
            return True
        else:
            print("⚠️  数据库验证失败")
            return False
    
    def close(self):
        self.client.close()

def main():
    verifier = DatabaseVerifier()
    try:
        result = verifier.run_full_verification()
        return result
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False
    finally:
        verifier.close()

if __name__ == "__main__":
    main() 