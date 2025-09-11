import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class HackerNewsScraper:
    """Hacker News 热门新闻抓取器"""
    
    def __init__(self):
        self.api_base_url = "https://hacker-news.firebaseio.com/v0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_trending_news(self, max_retries: int = 3) -> List[Dict]:
        """
        获取Hacker News热门新闻列表
        
        Args:
            max_retries: 最大重试次数
            
        Returns:
            新闻信息列表
        """
        logger.info(f"开始抓取Hacker News热门新闻，最大重试次数: {max_retries}")
        
        for attempt in range(max_retries):
            try:
                logger.info(f"尝试抓取 (第{attempt + 1}次)")
                
                # 1. 获取热门新闻ID列表
                top_story_ids = self._get_top_story_ids()
                if not top_story_ids:
                    logger.warning("未获取到热门新闻ID列表")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return []
                
                # 2. 获取新闻详细信息
                news_list = self._get_news_details(top_story_ids[:15])  # 获取前15个，后面筛选前10个
                
                if news_list:
                    # 按分数排序，取前10个
                    sorted_news = sorted(news_list, key=lambda x: x.get('score', 0), reverse=True)
                    top_10_news = sorted_news[:10]
                    
                    logger.info(f"成功抓取到 {len(top_10_news)} 条Hacker News热门新闻")
                    return top_10_news
                else:
                    logger.warning("未获取到任何新闻详细信息")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return []
                    
            except Exception as e:
                logger.error(f"抓取Hacker News失败 (第{attempt + 1}次): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return []
        
        logger.error("经过所有重试后仍未能成功抓取Hacker News数据")
        return []
    
    def _get_top_story_ids(self) -> List[int]:
        """获取热门新闻ID列表"""
        try:
            url = f"{self.api_base_url}/topstories.json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            story_ids = response.json()
            logger.info(f"获取到 {len(story_ids)} 个热门新闻ID")
            return story_ids
            
        except Exception as e:
            logger.error(f"获取热门新闻ID列表失败: {e}")
            return []
    
    def _get_news_details(self, story_ids: List[int]) -> List[Dict]:
        """获取新闻详细信息"""
        news_list = []
        
        for i, story_id in enumerate(story_ids):
            try:
                logger.info(f"正在获取新闻详情 {i+1}/{len(story_ids)}: ID {story_id}")
                
                # 获取新闻基本信息
                news_info = self._get_story_info(story_id)
                if not news_info:
                    continue
                
                # 获取新闻详细内容
                if news_info.get('url'):
                    content = self._scrape_news_content(news_info['url'])
                    news_info['content'] = content
                else:
                    news_info['content'] = ""
                
                news_list.append(news_info)
                
                # 添加延迟避免请求过快
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"获取新闻 {story_id} 详情失败: {e}")
                continue
        
        return news_list
    
    def _get_story_info(self, story_id: int) -> Optional[Dict]:
        """获取单个新闻的基本信息"""
        try:
            url = f"{self.api_base_url}/item/{story_id}.json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or data.get('type') != 'story':
                return None
            
            # 提取新闻信息
            news_info = {
                'id': story_id,
                'title': data.get('title', ''),
                'url': data.get('url', ''),
                'score': data.get('score', 0),
                'comments': data.get('descendants', 0),
                'time': data.get('time', 0),
                'by': data.get('by', ''),
                'content': ''  # 将在后续步骤中填充
            }
            
            return news_info
            
        except Exception as e:
            logger.error(f"获取新闻 {story_id} 基本信息失败: {e}")
            return None
    
    def _scrape_news_content(self, url: str) -> str:
        """抓取新闻详细内容"""
        try:
            # 跳过Hacker News内部链接
            if 'news.ycombinator.com' in url:
                return ""
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 尝试多种选择器来获取主要内容
            content_selectors = [
                'article',
                '.post-content',
                '.entry-content',
                '.content',
                '.article-content',
                'main',
                '.main-content',
                '[role="main"]'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    # 取第一个匹配的元素
                    content = elements[0].get_text(separator=' ', strip=True)
                    if len(content) > 100:  # 确保内容足够长
                        break
            
            # 如果没有找到合适的内容，尝试获取body内容
            if not content or len(content) < 100:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
            
            # 清理内容
            content = self._clean_content(content)
            
            # 限制内容长度，为翻译提供足够的内容
            if len(content) > 5000:
                content = content[:5000] + "..."
            
            return content
            
        except Exception as e:
            logger.warning(f"抓取新闻内容失败 {url}: {e}")
            return ""
    
    def _clean_content(self, content: str) -> str:
        """清理新闻内容"""
        if not content:
            return ""
        
        # 移除多余的空白字符
        import re
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        # 移除常见的无用文本
        unwanted_patterns = [
            r'Subscribe to.*?newsletter',
            r'Follow us on.*?social media',
            r'Share this article',
            r'Related articles',
            r'Advertisement',
            r'Advertisements',
            r'Cookie policy',
            r'Privacy policy',
            r'Terms of service',
            r'All rights reserved',
            r'Copyright.*?\d{4}',
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
