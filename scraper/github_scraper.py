import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import logging
import time
from config import Config

logger = logging.getLogger(__name__)

class GitHubTrendingScraper:
    """GitHub Trending页面抓取器"""
    
    def __init__(self):
        self.base_url = "https://github.com/trending"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_trending_repositories(self, language: str = "any", since: str = "daily", max_retries: int = 3) -> List[Dict]:
        """
        获取trending仓库列表
        
        Args:
            language: 编程语言筛选 (any, python, javascript, etc.)
            since: 时间范围 (daily, weekly, monthly)
            max_retries: 最大重试次数
            
        Returns:
            仓库信息列表
        """
        for attempt in range(max_retries):
            try:
                # 构建URL
                url = f"{self.base_url}"
                if language != "any":
                    url += f"/{language}"
                url += f"?since={since}"
                
                logger.info(f"正在抓取 (尝试 {attempt + 1}/{max_retries}): {url}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 查找所有仓库条目 - 使用多种选择器
                repo_articles = soup.find_all('article', class_='Box-row')
                
                if not repo_articles:
                    # 尝试其他可能的选择器
                    repo_articles = soup.find_all('div', class_='Box-row')
                
                if not repo_articles:
                    # 尝试更通用的选择器
                    repo_articles = soup.find_all('article')
                
                if not repo_articles:
                    logger.error("未找到仓库条目，可能是页面结构已变化")
                    logger.debug(f"页面内容预览: {soup.prettify()[:1000]}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # 指数退避
                        continue
                    return []
                
                repositories = []
                
                for article in repo_articles:
                    try:
                        repo_info = self._parse_repository_article(article)
                        if repo_info:
                            repositories.append(repo_info)
                    except Exception as e:
                        logger.warning(f"解析仓库信息时出错: {e}")
                        continue
                
                if repositories:
                    logger.info(f"成功抓取到 {len(repositories)} 个仓库")
                    return repositories
                else:
                    logger.warning("未解析到任何仓库信息")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return []
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"网络请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return []
            except Exception as e:
                logger.error(f"抓取GitHub trending页面失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return []
        
        logger.error(f"经过 {max_retries} 次尝试后仍未能成功抓取数据")
        return []
    
    def _parse_repository_article(self, article) -> Optional[Dict]:
        """解析单个仓库文章元素"""
        try:
            # 获取仓库链接和名称 - 使用多种选择器
            repo_name = None
            repo_url = None
            
            # 方法1: 查找h2标签
            repo_link_elem = article.find('h2', class_='h3 lh-condensed')
            if repo_link_elem:
                repo_link = repo_link_elem.find('a')
                if repo_link:
                    repo_url = repo_link.get('href', '')
                    repo_name = repo_url.strip('/')
            
            # 方法2: 如果方法1失败，尝试其他选择器
            if not repo_name:
                repo_link = article.find('a', href=re.compile(r'^/[^/]+/[^/]+$'))
                if repo_link:
                    repo_url = repo_link.get('href', '')
                    repo_name = repo_url.strip('/')
            
            # 方法3: 查找所有链接，筛选出仓库链接
            if not repo_name:
                all_links = article.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href', '')
                    if re.match(r'^/[^/]+/[^/]+$', href):
                        repo_url = href
                        repo_name = href.strip('/')
                        break
            
            if not repo_name:
                logger.warning("无法解析仓库名称")
                return None
            
            # 获取描述
            description = ""
            description_elem = article.find('p')
            if description_elem:
                description = description_elem.get_text().strip()
            
            # 获取编程语言
            language = "Unknown"
            language_elem = article.find('span', {'itemprop': 'programmingLanguage'})
            if language_elem:
                language = language_elem.get_text().strip()
            else:
                # 尝试其他语言选择器
                language_elem = article.find('span', class_=re.compile(r'.*language.*'))
                if language_elem:
                    language = language_elem.get_text().strip()
            
            # 获取星标数
            stars = 0
            stars_elem = article.find('a', href=re.compile(r'/stargazers'))
            if stars_elem:
                stars_text = stars_elem.get_text().strip()
                stars = self._parse_number(stars_text)
            
            # 获取fork数
            forks = 0
            forks_elem = article.find('a', href=re.compile(r'/forks'))
            if forks_elem:
                forks_text = forks_elem.get_text().strip()
                forks = self._parse_number(forks_text)
            
            # 获取今日星标数
            today_stars = 0
            today_stars_elem = article.find('span', class_='d-inline-block float-sm-right')
            if today_stars_elem:
                today_stars_text = today_stars_elem.get_text().strip()
                today_stars = self._parse_number(today_stars_text)
            
            # 获取标签
            topics = []
            topics_container = article.find('div', class_='f6 color-fg-muted mb-2')
            if topics_container:
                topic_links = topics_container.find_all('a', class_='topic-tag')
                topics = [link.get_text().strip() for link in topic_links]
            
            return {
                'name': repo_name,
                'url': f"https://github.com{repo_url}",
                'description': description,
                'language': language,
                'stars': stars,
                'forks': forks,
                'today_stars': today_stars,
                'topics': topics
            }
            
        except Exception as e:
            logger.error(f"解析仓库文章时出错: {e}")
            return None
    
    def _parse_number(self, text: str) -> int:
        """解析数字字符串"""
        try:
            if not text:
                return 0
            
            # 移除逗号、空格和k/m等后缀
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

