"""
数据库管理脚本 - 查询和管理MongoDB数据
功能：数据统计 -> 关键词搜索 -> 随机查询 -> 导出训练数据
"""
import json
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

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME')]
        self.collection = self.db[os.getenv('COLLECTION_NAME')]
        print("✅ MongoDB连接成功")
    
    def get_info(self):
        """获取数据库基本信息"""
        total = self.collection.count_documents({})
        chinese = self.collection.count_documents({'Context': {'$ne': ''}})
        english = self.collection.count_documents({'original_Context': {'$ne': ''}})
        indexes = [idx['name'] for idx in self.collection.list_indexes()]
        
        info = {
            'database': os.getenv('DATABASE_NAME'),
            'collection': os.getenv('COLLECTION_NAME'),
            'total_records': total,
            'chinese_records': chinese,
            'english_records': english,
            'indexes': indexes
        }
        
        print("📊 数据库信息:")
        print(f"   数据库: {info['database']}")
        print(f"   集合: {info['collection']}")
        print(f"   总记录: {info['total_records']}")
        print(f"   中文: {info['chinese_records']}")
        print(f"   英文: {info['english_records']}")
        print(f"   索引: {len(info['indexes'])}")
        
        return info
    
    def search(self, keyword, language='chinese', limit=5):
        """关键词搜索"""
        if language == 'chinese':
            query = {
                '$or': [
                    {'Context': {'$regex': keyword, '$options': 'i'}},
                    {'Response': {'$regex': keyword, '$options': 'i'}}
                ]
            }
        else:
            query = {
                '$or': [
                    {'original_Context': {'$regex': keyword, '$options': 'i'}},
                    {'original_Response': {'$regex': keyword, '$options': 'i'}}
                ]
            }
        
        results = list(self.collection.find(query).limit(limit))
        print(f"🔍 搜索'{keyword}' ({language}): {len(results)} 条结果")
        return results
    
    def get_random(self, count=3):
        """获取随机对话"""
        pipeline = [{'$sample': {'size': count}}]
        results = list(self.collection.aggregate(pipeline))
        print(f"🎲 随机获取: {len(results)} 条对话")
        return results
    
    def get_by_index(self, index):
        """根据索引获取对话"""
        result = self.collection.find_one({'translation_index': index})
        if result:
            print(f"📄 找到索引 {index} 的对话")
        else:
            print(f"❌ 未找到索引 {index} 的对话")
        return result
    
    def export_training_data(self, output_file=None):
        """导出训练数据"""
        if output_file is None:
            output_file = os.path.join(project_root, 'data', 'training_data.json')
        print(f"📤 导出训练数据到: {output_file}")
        
        # 获取所有数据
        cursor = self.collection.find({}, {
            '_id': 0,
            'Context': 1,
            'Response': 1,
            'original_Context': 1,
            'original_Response': 1,
            'translation_index': 1
        })
        
        # 转换格式
        training_data = []
        for item in cursor:
            training_sample = {
                'input': item.get('Context', ''),
                'output': item.get('Response', ''),
                'input_en': item.get('original_Context', ''),
                'output_en': item.get('original_Response', ''),
                'id': item.get('translation_index', 0)
            }
            training_data.append(training_sample)
        
        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 导出完成: {len(training_data)} 条训练样本")
        return len(training_data)
    
    def show_sample(self, data):
        """显示数据样本"""
        if not data:
            print("📭 无数据")
            return
        
        sample = data[0] if isinstance(data, list) else data
        print(f"📄 样本数据:")
        print(f"   索引: {sample.get('translation_index', 'N/A')}")
        print(f"   中文问题: {sample.get('Context', '')[:80]}...")
        print(f"   中文回答: {sample.get('Response', '')[:80]}...")
    
    def close(self):
        self.client.close()

def main():
    db = DatabaseManager()
    try:
        # 显示数据库信息
        db.get_info()
        print()
        
        # 演示搜索功能
        chinese_results = db.search("抑郁", "chinese", 3)
        english_results = db.search("depression", "english", 3)
        print()
        
        # 显示随机对话
        random_data = db.get_random(2)
        db.show_sample(random_data)
        print()
        
        # 导出训练数据
        count = db.export_training_data()
        print(f"🎉 管理操作完成！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 