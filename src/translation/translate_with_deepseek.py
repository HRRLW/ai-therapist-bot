import json
import os
import sys
import time
import logging
from typing import Dict, List, Any
import requests
from tqdm import tqdm
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# 加载配置文件
config_path = os.path.join(project_root, 'config', '.env')
load_dotenv(config_path)

# 设置日志目录
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'translation.log')),
        logging.StreamHandler()
    ]
)

class DeepSeekTranslator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def translate_text(self, text: str) -> str:
        """使用DeepSeek API翻译文本到中文"""
        try:
            if not text or text.strip() == "":
                return ""
            
            # 构建翻译提示
            prompt = f"""请将以下英文心理健康咨询对话翻译成中文，保持专业性和准确性，不要添加任何额外内容，只返回翻译结果：

{text}"""

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            # 发送请求
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()
                return translated_text
            else:
                logging.error(f"API请求失败: {response.status_code} - {response.text}")
                return text
                
        except Exception as e:
            logging.error(f"翻译错误: {e}")
            return text
    
    def translate_dataset(self, input_file: str, output_file: str):
        """翻译整个数据集"""
        logging.info(f"开始翻译数据集: {input_file}")
        
        # 读取英文数据
        with open(input_file, 'r', encoding='utf-8') as f:
            english_data = json.load(f)
        
        logging.info(f"找到 {len(english_data)} 条对话记录")
        
        # 翻译数据
        chinese_data = []
        success_count = 0
        
        for i, item in enumerate(tqdm(english_data, desc="翻译进度")):
            try:
                # 翻译Context和Response
                context_zh = self.translate_text(item.get('Context', ''))
                response_zh = self.translate_text(item.get('Response', ''))
                
                # 创建中文记录
                chinese_item = {
                    'Context': context_zh,
                    'Response': response_zh,
                    'original_Context': item.get('Context', ''),
                    'original_Response': item.get('Response', ''),
                    'translation_index': i + 1
                }
                
                chinese_data.append(chinese_item)
                success_count += 1
                
                # 避免API限制，添加延迟
                time.sleep(0.5)
                
                # 每100条保存一次进度
                if (i + 1) % 100 == 0:
                    self._save_progress(chinese_data, f"{output_file}.progress_{i+1}")
                    logging.info(f"已完成 {i+1} 条翻译，保存进度文件")
                
            except Exception as e:
                logging.error(f"翻译第 {i+1} 条记录时出错: {e}")
                # 出错时保存原文
                chinese_item = {
                    'Context': item.get('Context', ''),
                    'Response': item.get('Response', ''),
                    'original_Context': item.get('Context', ''),
                    'original_Response': item.get('Response', ''),
                    'translation_index': i + 1,
                    'translation_error': True
                }
                chinese_data.append(chinese_item)
                continue
        
        # 保存最终结果
        self._save_progress(chinese_data, output_file)
        
        logging.info(f"翻译完成！")
        logging.info(f"成功翻译: {success_count}/{len(english_data)} 条记录")
        logging.info(f"中文数据集已保存到: {output_file}")
        
        return chinese_data
    
    def _save_progress(self, data: List[Dict], filename: str):
        """保存翻译进度"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    # 检查API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        logging.error("请在.env文件中设置DEEPSEEK_API_KEY")
        return
    
    # 初始化翻译器
    translator = DeepSeekTranslator(api_key)
    
    # 设置文件路径 - 更新为新的文件结构
    input_file = os.path.join(project_root, "data", "main", "dataset_english.json")
    output_file = os.path.join(project_root, "data", "main", "dataset_chinese.json")
    
    # 检查输入文件
    if not os.path.exists(input_file):
        logging.error(f"输入文件不存在: {input_file}")
        return
    
    # 开始翻译
    try:
        chinese_data = translator.translate_dataset(input_file, output_file)
        
        # 显示统计信息
        logging.info(f"翻译完成统计:")
        logging.info(f"- 输入文件: {input_file}")
        logging.info(f"- 输出文件: {output_file}")
        logging.info(f"- 总记录数: {len(chinese_data)}")
        
        # 显示示例
        if chinese_data:
            sample = chinese_data[0]
            logging.info(f"\n示例翻译:")
            logging.info(f"原文Context: {sample.get('original_Context', '')[:100]}...")
            logging.info(f"中文Context: {sample.get('Context', '')[:100]}...")
            
    except Exception as e:
        logging.error(f"翻译过程中出错: {e}")

if __name__ == "__main__":
    main() 