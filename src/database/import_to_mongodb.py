"""
数据库导入脚本 - 将中文数据导入MongoDB
功能：清理旧数据 -> 导入新数据 -> 创建索引 -> 验证结果
"""
import json
import os
import sys
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from tqdm import tqdm

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# 加载配置文件
config_path = os.path.join(project_root, 'config', '.env')
load_dotenv(config_path)

class DatabaseImporter:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME')]
        self.collection = self.db[os.getenv('COLLECTION_NAME')]
        print("✅ MongoDB连接成功")
    
    def clear_data(self):
        """清理现有数据"""
        count = self.collection.count_documents({})
        if count > 0:
            self.collection.delete_many({})
            print(f"🗑️  已清理 {count} 条旧数据")
        else:
            print("📭 无需清理数据")
    
    def import_data(self, file_path):
        """导入数据"""
        print(f"📥 开始导入: {file_path}")
        
        # 读取数据
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加导入时间戳
        import_time = time.time()
        for item in data:
            item['imported_at'] = import_time
        
        # 批量插入
        batch_size = 100
        total = 0
        for i in tqdm(range(0, len(data), batch_size), desc="导入进度"):
            batch = data[i:i + batch_size]
            result = self.collection.insert_many(batch)
            total += len(result.inserted_ids)
        
        print(f"✅ 导入完成: {total} 条记录")
        return total
    
    def create_indexes(self):
        """创建索引"""
        print("🔧 创建索引...")
        self.collection.create_index("translation_index")
        self.collection.create_index("imported_at")
        print("✅ 索引创建完成")
    
    def verify(self):
        """验证导入结果"""
        total = self.collection.count_documents({})
        chinese = self.collection.count_documents({'Context': {'$ne': ''}})
        english = self.collection.count_documents({'original_Context': {'$ne': ''}})
        
        print(f"📊 验证结果:")
        print(f"   总记录: {total}")
        print(f"   中文记录: {chinese}")
        print(f"   英文记录: {english}")
        
        return total == chinese == english
    
    def close(self):
        self.client.close()

def main():
    importer = DatabaseImporter()
    try:
        # 执行导入流程
        importer.clear_data()
        data_path = os.path.join(project_root, "data", "main", "dataset_chinese.json")
        importer.import_data(data_path)
        importer.create_indexes()
        
        # 验证结果
        if importer.verify():
            print("🎉 数据库构建成功！")
        else:
            print("⚠️  数据验证失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        importer.close()

if __name__ == "__main__":
    main() 