#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub 每日趋势项目工具
自动抓取GitHub trending页面，翻译项目描述，生成Markdown文档
"""

import logging
import sys
from datetime import datetime
from typing import List, Dict

from config import Config
from scraper.github_scraper import GitHubTrendingScraper
from scraper.producthunt_scraper import ProductHuntScraper
from scraper.translator import DeepSeekTranslator
from scraper.markdown_generator import MarkdownGenerator
from build_site import MkDocsBuilder

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_trending.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DayHotTool:
    """每日热门工具主类"""
    
    def __init__(self):
        """初始化工具"""
        try:
            # 验证配置
            Config.validate()
            
            # 初始化组件
            self.github_scraper = GitHubTrendingScraper()
            self.producthunt_scraper = ProductHuntScraper()
            self.translator = DeepSeekTranslator()
            self.markdown_generator = MarkdownGenerator()
            self.site_builder = MkDocsBuilder()
            
            logger.info("每日热门工具初始化成功")
            
        except Exception as e:
            logger.error(f"工具初始化失败: {e}")
            raise
    
    def run_daily_task(self, language: str = "any", since: str = "daily") -> bool:
        """
        执行每日任务
        
        Args:
            language: 编程语言筛选
            since: 时间范围
            
        Returns:
            任务是否成功
        """
        try:
            logger.info("开始执行每日热门任务")
            current_date = datetime.now()
            
            # 1. 抓取GitHub trending数据
            logger.info("步骤1: 抓取GitHub trending数据")
            github_repos = self.github_scraper.get_trending_repositories(language, since)
            
            if not github_repos:
                logger.error("未获取到任何GitHub仓库数据")
                github_repos = []
                # return False
            else:
                logger.info(f"成功抓取到 {len(github_repos)} 个GitHub仓库")
            
            # 2. 抓取ProductHunt数据
            logger.info("步骤2: 抓取ProductHunt数据")
            producthunt_products = self.producthunt_scraper.get_trending_products()
            
            if not producthunt_products:
                logger.warning("未获取到任何ProductHunt产品数据")
                producthunt_products = []
            else:
                logger.info(f"成功抓取到 {len(producthunt_products)} 个ProductHunt产品")
            
            # 3. 翻译项目描述
            logger.info("步骤3: 翻译项目描述")
            translated_github_repos = self.translator.translate_repositories(github_repos)
            translated_producthunt_products = self.translator.translate_products(producthunt_products)
            
            logger.info(f"成功翻译 {len(translated_github_repos)} 个GitHub仓库的描述")
            logger.info(f"成功翻译 {len(translated_producthunt_products)} 个ProductHunt产品的描述")
            
            # 4. 生成Markdown文件
            logger.info("步骤4: 生成Markdown文件")
            
            # 生成GitHub每日详细文件
            github_file = self.markdown_generator.generate_daily_trending_markdown(
                translated_github_repos, current_date
            )
            
            # 生成ProductHunt每日详细文件
            producthunt_file = self.markdown_generator.generate_daily_producthunt_markdown(
                translated_producthunt_products, current_date
            )
            
            # 生成首页文件
            self.markdown_generator.generate_today_file(
                translated_github_repos, translated_producthunt_products, current_date
            )
            
            # 生成历史记录页面
            self.markdown_generator.generate_github_history_page()
            self.markdown_generator.generate_producthunt_history_page()
            
            if github_file and producthunt_file:
                logger.info("Markdown文件生成成功")
                logger.info(f"GitHub文件: {github_file}")
                logger.info(f"ProductHunt文件: {producthunt_file}")
                
                # 5. 构建网站
                logger.info("步骤5: 构建MkDocs网站")
                if self.site_builder.build_site():
                    logger.info("网站构建成功！")
                else:
                    logger.warning("网站构建失败，但Markdown文件已生成")
            else:
                logger.error("Markdown文件生成失败")
                return False
            
            logger.info("每日热门任务执行完成")
            return True
            
        except Exception as e:
            logger.error(f"执行每日任务时出错: {e}")
            return False
    
    def run_once(self, language: str = "any", since: str = "daily") -> bool:
        """
        执行一次任务（用于手动运行）
        
        Args:
            language: 编程语言筛选
            since: 时间范围
            
        Returns:
            任务是否成功
        """
        return self.run_daily_task(language, since)

def main():
    """主函数"""
    try:
        # 创建工具实例
        tool = DayHotTool()
        
        # 执行任务
        success = tool.run_once()
        
        if success:
            logger.info("任务执行成功！")
            sys.exit(0)
        else:
            logger.error("任务执行失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("用户中断任务")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

