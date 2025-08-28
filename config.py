import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    
    # 输出路径配置
    OUTPUT_DIR = os.path.join('./mkdocs')
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
        
        # 确保输出目录存在
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        
        return True

