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
    
    def translate_products(self, products: List[Dict]) -> List[Dict]:
        """
        批量翻译产品信息
        
        Args:
            products: 产品信息列表
            
        Returns:
            包含中文翻译的产品信息列表
        """
        translated_products = []
        
        for i, product in enumerate(products):
            try:
                logger.info(f"正在翻译第 {i+1}/{len(products)} 个产品: {product['name']}")
                
                # 翻译描述
                if product.get('description'):
                    product['description_zh'] = self.translate_text(product['description'])
                else:
                    product['description_zh'] = ""
                
                # 添加延迟避免API限制
                time.sleep(1)
                
                translated_products.append(product)
                
            except Exception as e:
                logger.error(f"翻译产品 {product['name']} 时出错: {e}")
                # 如果翻译失败，保留原文
                product['description_zh'] = product.get('description', '')
                translated_products.append(product)
        
        return translated_products
    
    def translate_news(self, news_list: List[Dict]) -> List[Dict]:
        """
        批量翻译和总结新闻信息
        
        Args:
            news_list: 新闻信息列表
            
        Returns:
            包含中文总结的新闻信息列表
        """
        translated_news = []
        
        for i, news in enumerate(news_list):
            try:
                logger.info(f"正在处理第 {i+1}/{len(news_list)} 条新闻: {news.get('title', 'Unknown')[:50]}...")
                
                # 生成新闻总结
                summary = self.summarize_news_content(
                    news.get('content', ''), 
                    news.get('title', '')
                )
                news['summary_zh'] = summary
                
                # 添加延迟避免API限制
                time.sleep(1)
                
                translated_news.append(news)
                
            except Exception as e:
                logger.error(f"处理新闻 {news.get('title', 'Unknown')} 时出错: {e}")
                # 如果处理失败，保留原文
                news['summary_zh'] = news.get('title', '')
                translated_news.append(news)
        
        return translated_news
    
    def summarize_news_content(self, content: str, title: str = "") -> str:
        """
        总结新闻内容
        
        Args:
            content: 新闻内容
            title: 新闻标题
            
        Returns:
            中文总结（10-200字）
        """
        if not content and not title:
            return "暂无内容"
        
        try:
            # 构建总结提示词
            prompt = f"""请将以下新闻内容翻译并总结成10-200字的中文摘要，要求：
1. 准确翻译原文内容
2. 突出核心信息和关键点
3. 语言流畅自然
4. 字数控制在10-200字之间
5. 如果内容较短，请提供更详细的翻译和解释

标题：{title}

内容：{content[:5000] if content else '无详细内容'}

请直接给出中文总结，不要添加任何解释或前缀："""
            
            response = self._call_deepseek_api(prompt)
            
            if response:
                # 清理响应内容
                summary = response.strip()
                
                # 移除可能的"总结："等前缀
                prefixes = ["总结：", "摘要：", "概括：", "翻译：", "总结", "摘要", "概括", "翻译"]
                for prefix in prefixes:
                    if summary.startswith(prefix):
                        summary = summary[len(prefix):].strip()
                
                # 确保字数在10-200字之间
                if len(summary) < 10:
                    # 如果太短，尝试用标题补充
                    if title and len(title) > 5:
                        summary = f"{title}：{summary}"
                    else:
                        summary = summary + "（详细内容请查看原文）"
                elif len(summary) > 200:
                    summary = summary[:200] + "..."
                
                return summary
            else:
                # 如果API调用失败，返回标题的翻译版本
                if title:
                    return f"{title}（详细内容请查看原文）"
                else:
                    return "内容总结失败"
                    
        except Exception as e:
            logger.error(f"总结新闻内容出错: {e}")
            # 返回标题作为备选
            if title:
                return f"{title}（详细内容请查看原文）"
            else:
                return "总结失败"
    
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

