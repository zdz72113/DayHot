import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import logging
import time
import json
import os
from datetime import datetime, timezone, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import Config

logger = logging.getLogger(__name__)

class ProductHuntScraper:
    """ProductHunt热门产品抓取器"""
    
    def __init__(self):
        self.base_url = "https://www.producthunt.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 设置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def get_producthunt_token(self):
        """获取 Product Hunt 访问令牌"""
        # 优先使用 PRODUCTHUNT_DEVELOPER_TOKEN 环境变量
        developer_token = os.getenv('PRODUCTHUNT_DEVELOPER_TOKEN')
        if developer_token:
            logger.info("使用 PRODUCTHUNT_DEVELOPER_TOKEN 环境变量")
            return developer_token
        
        # 如果没有 developer token，尝试使用 client credentials 获取访问令牌
        client_id = os.getenv('PRODUCTHUNT_CLIENT_ID')
        client_secret = os.getenv('PRODUCTHUNT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.warning("Product Hunt client ID or client secret not found in environment variables")
            return None
        
        # 使用 client credentials 获取访问令牌
        token_url = "https://api.producthunt.com/v2/oauth/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        
        try:
            response = self.session.post(token_url, json=payload)
            response.raise_for_status()
            token_data = response.json()
            return token_data.get("access_token")
        except Exception as e:
            logger.error(f"获取 Product Hunt 访问令牌时出错: {e}")
            return None
    
    def get_trending_products(self, max_retries: int = 3) -> List[Dict]:
        """获取ProductHunt热门产品列表"""
        # 首先尝试使用API
        try:
            products = self._fetch_from_api()
            if products:
                logger.info(f"成功从API抓取到 {len(products)} 个产品")
                return products[:10]  # 只返回前10个
        except Exception as e:
            logger.warning(f"API抓取失败: {e}")

        return []
        
        # # 如果API失败，尝试网页抓取
        # try:
        #     products = self._scrape_webpage()
        #     if products:
        #         logger.info(f"成功从网页抓取到 {len(products)} 个产品")
        #         return products[:10]  # 只返回前10个
        # except Exception as e:
        #     logger.warning(f"网页抓取失败: {e}")
        
        # # 如果都失败了，返回模拟数据
        # logger.warning("所有抓取方法都失败，使用模拟数据")
        # return self._generate_mock_products()
    
    def _fetch_from_api(self) -> List[Dict]:
        """从Product Hunt API获取数据"""
        token = self.get_producthunt_token()
        if not token:
            raise Exception("无法获取Product Hunt访问令牌")
        
        # 获取昨天的数据
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
        url = "https://api.producthunt.com/v2/api/graphql"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "DayHotBot/1.0",
            "Origin": "https://dayhot.com",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "keep-alive"
        }

        base_query = """
        {
          posts(order: VOTES, postedAfter: "%sT00:00:00Z", postedBefore: "%sT23:59:59Z", after: "%s") {
            nodes {
              id
              name
              tagline
              description
              votesCount
              createdAt
              featuredAt
              website
              url
              media {
                url
                type
                videoUrl
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """

        all_posts = []
        has_next_page = True
        cursor = ""

        while has_next_page and len(all_posts) < 30:
            query = base_query % (date_str, date_str, cursor)
            try:
                response = self.session.post(url, headers=headers, json={"query": query})
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"API请求失败: {e}")
                raise Exception(f"Failed to fetch data from Product Hunt API: {e}")

            data = response.json()
            if 'data' not in data or 'posts' not in data['data']:
                logger.error(f"API返回数据格式错误: {data}")
                raise Exception("Invalid API response format")

            posts_data = data['data']['posts']
            posts = posts_data['nodes']
            all_posts.extend(posts)

            has_next_page = posts_data['pageInfo']['hasNextPage']
            cursor = posts_data['pageInfo']['endCursor']

        # 按投票数排序并转换为标准格式
        sorted_posts = sorted(all_posts, key=lambda x: x.get('votesCount', 0), reverse=True)
        products = []
        
        for post in sorted_posts[:10]:  # 只取前10个
            product_info = {
                'name': post.get('name', ''),
                'url': post.get('url', ''),
                'description': post.get('description', ''),
                'tags': [],  # API中没有直接提供标签
                'votes': post.get('votesCount', 0)
            }
            if product_info['name']:
                products.append(product_info)
        
        return products
    
    def _scrape_webpage(self) -> List[Dict]:
        """从网页抓取产品信息"""
        try:
            url = "https://www.producthunt.com"
            logger.info(f"正在抓取ProductHunt网页: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找产品卡片
            products = []
            
            # 尝试多种选择器
            selectors = [
                '[data-test="post-item"]',
                '[data-test="post-card"]',
                '.post-item',
                '.post-card',
                'article[data-test*="post"]',
                'div[class*="PostItem"]',
                'div[class*="ProductCard"]'
            ]
            
            product_elements = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    product_elements = elements[:10]  # 只取前10个
                    logger.info(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                    break
            
            # 如果还是找不到，尝试查找包含产品链接的元素
            if not product_elements:
                product_links = soup.find_all('a', href=re.compile(r'/posts/'))
                if product_links:
                    parent_elements = set()
                    for link in product_links[:20]:
                        parent = link.find_parent('div') or link.find_parent('article')
                        if parent:
                            parent_elements.add(parent)
                    product_elements = list(parent_elements)[:10]
                    logger.info(f"通过产品链接找到 {len(product_elements)} 个元素")
            
            # 解析产品信息
            for element in product_elements:
                try:
                    product_info = self._parse_product_element(element)
                    if product_info:
                        products.append(product_info)
                except Exception as e:
                    logger.warning(f"解析产品元素时出错: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"网页抓取失败: {e}")
            return []
    
    def _parse_product_element(self, element) -> Optional[Dict]:
        """解析单个产品元素"""
        try:
            # 获取产品名称
            name = ""
            name_selectors = ['h3', 'h2', 'h1', '[data-test="post-name"]', '.post-name']
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text().strip()
                    break
            
            # 获取产品链接
            url = ""
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    url = f"{self.base_url}{href}"
                else:
                    url = href
            
            # 获取产品描述
            description = ""
            desc_selectors = ['p', '[data-test="post-tagline"]', '.post-tagline', '.description']
            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text().strip()
                    break
            
            # 获取标签
            tags = []
            tag_elements = element.find_all('a', class_=re.compile(r'.*tag.*'))
            for tag_elem in tag_elements:
                tag_text = tag_elem.get_text().strip()
                if tag_text:
                    tags.append(tag_text)
            
            # 获取投票数
            votes = 0
            votes_selectors = ['[data-test="vote-count"]', '.vote-count', 'span[class*="vote"]']
            for selector in votes_selectors:
                votes_elem = element.select_one(selector)
                if votes_elem:
                    votes_text = votes_elem.get_text().strip()
                    votes = self._parse_number(votes_text)
                    break
            
            # 如果没有找到基本信息，尝试备用方法
            if not name and not description:
                all_text = element.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                if lines:
                    name = lines[0][:100]
                    if len(lines) > 1:
                        description = lines[1][:200]
            
            if not name:
                return None
            
            return {
                'name': name,
                'url': url,
                'description': description,
                'tags': tags,
                'votes': votes
            }
            
        except Exception as e:
            logger.error(f"解析产品元素时出错: {e}")
            return None
    
    def _parse_number(self, text: str) -> int:
        """解析数字字符串"""
        try:
            if not text:
                return 0
            
            text = text.replace(',', '').replace(' ', '').lower()
            
            if 'k' in text:
                text = text.replace('k', '')
                return int(float(text) * 1000)
            elif 'm' in text:
                text = text.replace('m', '')
                return int(float(text) * 1000000)
            else:
                return int(float(text))
        except:
            return 0
    
    def _generate_mock_products(self) -> List[Dict]:
        """生成模拟的ProductHunt产品数据用于测试"""
        mock_products = [
            {
                'name': 'AI Writing Assistant',
                'url': 'https://www.producthunt.com/posts/ai-writing-assistant',
                'description': 'An intelligent writing assistant that helps you create better content with AI-powered suggestions and grammar checking.',
                'tags': ['AI', 'Productivity', 'Writing'],
                'votes': 245
            },
            {
                'name': 'TaskFlow Pro',
                'url': 'https://www.producthunt.com/posts/taskflow-pro',
                'description': 'A powerful project management tool designed for remote teams to collaborate effectively and track progress in real-time.',
                'tags': ['Productivity', 'Project Management', 'Collaboration'],
                'votes': 189
            },
            {
                'name': 'DesignHub',
                'url': 'https://www.producthunt.com/posts/designhub',
                'description': 'All-in-one design platform for creating stunning graphics, prototypes, and user interfaces with advanced collaboration features.',
                'tags': ['Design', 'Prototyping', 'UI/UX'],
                'votes': 312
            },
            {
                'name': 'CodeSync',
                'url': 'https://www.producthunt.com/posts/codesync',
                'description': 'Real-time code collaboration platform that allows developers to work together seamlessly with live editing and version control.',
                'tags': ['Development', 'Collaboration', 'Code'],
                'votes': 156
            },
            {
                'name': 'DataViz Studio',
                'url': 'https://www.producthunt.com/posts/dataviz-studio',
                'description': 'Advanced data visualization tool that transforms complex data into beautiful, interactive charts and dashboards.',
                'tags': ['Data', 'Analytics', 'Visualization'],
                'votes': 203
            },
            {
                'name': 'SecureChat',
                'url': 'https://www.producthunt.com/posts/securechat',
                'description': 'End-to-end encrypted messaging app with advanced security features for businesses and individuals.',
                'tags': ['Security', 'Communication', 'Privacy'],
                'votes': 178
            },
            {
                'name': 'EcoTracker',
                'url': 'https://www.producthunt.com/posts/ecotracker',
                'description': 'Personal carbon footprint tracker that helps you monitor and reduce your environmental impact through smart insights.',
                'tags': ['Sustainability', 'Health', 'Environment'],
                'votes': 134
            },
            {
                'name': 'LearnFlow',
                'url': 'https://www.producthunt.com/posts/learnflow',
                'description': 'Adaptive learning platform that personalizes educational content based on your learning style and progress.',
                'tags': ['Education', 'Learning', 'Personalization'],
                'votes': 267
            },
            {
                'name': 'FinanceWise',
                'url': 'https://www.producthunt.com/posts/financewise',
                'description': 'Smart financial planning app that helps you budget, invest, and achieve your financial goals with AI-powered insights.',
                'tags': ['Finance', 'Budgeting', 'Investment'],
                'votes': 198
            },
            {
                'name': 'HealthSync',
                'url': 'https://www.producthunt.com/posts/healthsync',
                'description': 'Comprehensive health monitoring app that syncs with your devices to track fitness, nutrition, and wellness metrics.',
                'tags': ['Health', 'Fitness', 'Wellness'],
                'votes': 223
            }
        ]
        
        logger.info(f"生成了 {len(mock_products)} 个模拟ProductHunt产品")
        return mock_products
