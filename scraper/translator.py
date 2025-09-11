import requests
import json
import time
from typing import List, Dict, Optional
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
        批量翻译仓库信息（增强版）
        
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
                
                # 分析仓库内容并提取特性和场景
                if repo.get('readme_content'):
                    try:
                        analysis_result = self.analyze_repository_content(repo)
                        if analysis_result:
                            repo.update(analysis_result)
                    except Exception as e:
                        logger.warning(f"分析仓库 {repo['name']} 内容失败: {e}")
                        # 分析失败时，设置默认值
                        repo['features'] = []
                        repo['features_zh'] = []
                        repo['use_cases'] = ""
                        repo['use_cases_zh'] = ""
                        repo['core_value_zh'] = ""
                        repo['use_cases_zh'] = ""
                else:
                    # 没有README内容时，设置默认值
                    repo['features'] = []
                    repo['features_zh'] = []
                    repo['use_cases'] = ""
                    repo['use_cases_zh'] = ""
                    repo['core_value_zh'] = ""
                    repo['use_cases_zh'] = ""
                
                # 添加延迟避免API限制
                time.sleep(1)
                
                translated_repos.append(repo)
                
            except Exception as e:
                logger.error(f"翻译仓库 {repo['name']} 时出错: {e}")
                # 如果翻译失败，保留原文
                repo['description_zh'] = repo.get('description', '')
                repo['features'] = []
                repo['features_zh'] = []
                repo['use_cases'] = ""
                repo['use_cases_zh'] = ""
                repo['core_value_zh'] = ""
                repo['use_cases_zh'] = ""
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
    
    def analyze_repository_content(self, repo_data: Dict) -> Optional[Dict]:
        """
        分析仓库内容并提取特性和应用场景
        
        Args:
            repo_data: 仓库数据
            
        Returns:
            包含特性和场景的字典
        """
        try:
            readme_content = repo_data.get('readme_content', '')
            description = repo_data.get('description', '')
            name = repo_data.get('name', '')
            
            if not readme_content:
                return None
            
            # 构建分析提示词
            prompt = f"""请分析以下GitHub项目的内容，提取主要特性和应用场景：

项目名称：{name}
项目描述：{description}

README内容：
{readme_content[:3000]}

请按以下格式返回分析结果（JSON格式）：
{{
    "features": ["特性1", "特性2", "特性3", "特性4", "特性5"],
    "use_cases": "应用场景描述（50-100字）"
}}

要求：
1. 提取3-5个主要特性，每个特性简洁明了
2. 应用场景描述控制在50-100字
3. 只返回JSON格式，不要其他内容"""
            
            response = self._call_deepseek_api(prompt)
            
            if response:
                try:
                    # 尝试解析JSON响应
                    import json
                    analysis = json.loads(response.strip())
                    
                    # 验证返回格式
                    if 'features' in analysis and 'use_cases' in analysis:
                        features = analysis['features']
                        use_cases = analysis['use_cases']
                        
                        # 翻译特性和场景
                        features_zh = []
                        for feature in features:
                            feature_zh = self.translate_text(feature)
                            features_zh.append(feature_zh)
                        
                        use_cases_zh = self.translate_text(use_cases)
                        
                        # 生成核心价值和适用场景
                        enhanced_info = self._generate_enhanced_description(
                            repo_data.get('description_zh', ''), features_zh, use_cases_zh
                        )
                        
                        return {
                            'features': features,
                            'features_zh': features_zh,
                            'use_cases': use_cases,
                            'use_cases_zh': use_cases_zh,
                            'core_value_zh': enhanced_info.get('core_value_zh', ''),
                            'use_cases_zh': enhanced_info.get('use_cases_zh', '')
                        }
                except json.JSONDecodeError:
                    logger.warning(f"解析仓库 {name} 分析结果失败")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"分析仓库内容出错: {e}")
            return None
    
    def _generate_enhanced_description(self, description_zh: str, features_zh: List[str], use_cases_zh: str) -> Dict:
        """
        生成增强描述（核心价值和适用场景）
        
        Args:
            description_zh: 中文描述
            features_zh: 中文特性列表
            use_cases_zh: 中文应用场景
            
        Returns:
            包含核心价值和适用场景的字典
        """
        try:
            # 构建分析提示词
            features_text = "、".join(features_zh[:3])  # 只取前3个特性
            
            prompt = f"""请从以下信息中提取核心价值点和适用场景：

项目描述：{description_zh}

主要特性：{features_text}

应用场景：{use_cases_zh}

要求：
1. 核心价值：用1-2句话概括项目的核心价值（20-30字）
2. 适用场景：列出2-3个主要应用场景，用"、"分隔（20-40字）
3. 语言简洁明了，突出重点

请按以下格式返回：
核心价值：[核心价值描述]
适用场景：[适用场景描述]"""
            
            response = self._call_deepseek_api(prompt)
            
            if response:
                # 解析响应
                lines = response.strip().split('\n')
                core_value = ""
                use_cases = ""
                
                for line in lines:
                    if line.startswith('核心价值：'):
                        core_value = line.replace('核心价值：', '').strip()
                    elif line.startswith('适用场景：'):
                        use_cases = line.replace('适用场景：', '').strip()
                
                # 确保长度在合理范围内
                if len(core_value) > 30:
                    core_value = core_value[:30] + "..."
                if len(use_cases) > 40:
                    use_cases = use_cases[:40] + "..."
                
                return {
                    'core_value_zh': core_value,
                    'use_cases_zh': use_cases
                }
            else:
                # API调用失败时，手动生成
                features_text = "、".join(features_zh[:2])  # 只取前2个特性
                core_value = f"提供{features_text}等核心功能"
                use_cases = "开发参考、学习研究、项目应用"
                
                return {
                    'core_value_zh': core_value,
                    'use_cases_zh': use_cases
                }
                
        except Exception as e:
            logger.error(f"生成增强描述出错: {e}")
            # 出错时返回默认值
            return {
                'core_value_zh': "提供核心功能和服务",
                'use_cases_zh': "开发参考、学习研究、项目应用"
            }
    
    def summarize_news_content(self, content: str, title: str = "") -> str:
        """
        总结新闻内容
        
        Args:
            content: 新闻内容
            title: 新闻标题
            
        Returns:
            中文总结（10-120字）
        """
        if not content and not title:
            return "暂无内容"
        
        try:
            # 构建总结提示词
            prompt = f"""请将以下新闻内容翻译并总结成10-120字的中文摘要，要求：
1. 准确翻译原文内容
2. 突出核心信息和关键点
3. 语言流畅自然
4. 字数控制在10-120字之间
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
                
                # 确保字数在10-120字之间
                if len(summary) < 10:
                    # 如果太短，尝试用标题补充
                    if title and len(title) > 5:
                        summary = f"{title}：{summary}"
                    else:
                        summary = summary + "（详细内容请查看原文）"
                elif len(summary) > 120:
                    summary = summary[:120] + "..."
                
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

