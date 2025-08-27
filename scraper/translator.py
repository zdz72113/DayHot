import requests
import json
import time
from typing import List, Dict
import logging
from config import Config

logger = logging.getLogger(__name__)

class DeepSeekTranslator:
    """使用DeepSeek API进行翻译"""
    
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = Config.DEEPSEEK_BASE_URL
        
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
    
    def translate_text(self, text: str, target_language: str = "中文") -> str:
        """
        翻译单个文本
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言
            
        Returns:
            翻译后的文本
        """
        if not text or text.strip() == "":
            return text
        
        try:
            prompt = f"""请将以下英文文本翻译成{target_language}，保持专业性和准确性，只翻译原文本身，不要添加任何其他内容，包括翻译说明和策略等：

原文：{text}

翻译："""
            
            response = self._call_deepseek_api(prompt)
            
            if response:
                # 提取翻译结果
                translated = response.strip()
                # 移除可能的"翻译："前缀
                if translated.startswith("翻译："):
                    translated = translated[3:].strip()
                
                # logger.info(f"翻译成功: {text[:50]}... -> {translated[:50]}...")
                return translated
            else:
                logger.warning(f"翻译失败，返回原文: {text}")
                return text
                
        except Exception as e:
            logger.error(f"翻译出错: {e}")
            return text
    
    def translate_repositories(self, repositories: List[Dict]) -> List[Dict]:
        """
        批量翻译仓库信息
        
        Args:
            repositories: 仓库信息列表
            
        Returns:
            包含中文翻译的仓库信息列表
        """
        translated_repos = []
        
        for i, repo in enumerate(repositories):
            try:
                logger.info(f"正在翻译第 {i+1}/{len(repositories)} 个仓库: {repo['name']}")
                
                # 翻译描述
                if repo.get('description'):
                    repo['description_zh'] = self.translate_text(repo['description'])
                else:
                    repo['description_zh'] = ""
                
                # 添加延迟避免API限制
                time.sleep(1)
                
                translated_repos.append(repo)
                
            except Exception as e:
                logger.error(f"翻译仓库 {repo['name']} 时出错: {e}")
                # 如果翻译失败，保留原文
                repo['description_zh'] = repo.get('description', '')
                translated_repos.append(repo)
        
        return translated_repos
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """
        调用DeepSeek API
        
        Args:
            prompt: 提示词
            
        Returns:
            API响应文本
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'deepseek-chat',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.3,
                'max_tokens': 1000
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"API响应格式错误: {result}")
                return ""
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            return ""
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return ""
        except Exception as e:
            logger.error(f"API调用出错: {e}")
            return ""

