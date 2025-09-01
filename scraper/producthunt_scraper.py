import requests
from typing import List, Dict
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
        """获取ProductHunt热门产品列表，带重试机制"""
        logger.info(f"开始抓取ProductHunt热门产品，最大重试次数: {max_retries}")
        
        # 尝试使用API抓取
        for attempt in range(max_retries):
            try:
                logger.info(f"尝试API抓取 (第{attempt + 1}次)")
                products = self._fetch_from_api()
                if products:
                    logger.info(f"成功从API抓取到 {len(products)} 个产品")
                    return products[:10]  # 只返回前10个
            except Exception as e:
                logger.warning(f"API抓取失败 (第{attempt + 1}次): {e}")
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    time.sleep(wait_time)
        
        # 如果所有重试都失败，返回空列表
        logger.error("API抓取失败，所有重试都已完成")
        return []
    
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
    

