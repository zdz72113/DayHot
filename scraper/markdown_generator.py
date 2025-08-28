from datetime import datetime
from typing import List, Dict
import os
import logging
import glob
from config import Config

logger = logging.getLogger(__name__)

class MarkdownGenerator:
    """Markdown文件生成器"""
    
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
    
    def generate_daily_trending_markdown(self, repositories: List[Dict], date: datetime = None) -> str:
        """生成每日GitHub trending的Markdown文件"""
        if date is None:
            date = datetime.now()
        
        filename = f"github-trending-{date.strftime('%Y-%m-%d')}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            content = self._generate_github_markdown_content(repositories, date)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"GitHub Markdown文件已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成GitHub Markdown文件失败: {e}")
            return ""
    
    def generate_daily_producthunt_markdown(self, products: List[Dict], date: datetime = None) -> str:
        """生成每日ProductHunt的Markdown文件"""
        if date is None:
            date = datetime.now()
        
        filename = f"producthunt-{date.strftime('%Y-%m-%d')}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            content = self._generate_producthunt_markdown_content(products, date)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"ProductHunt Markdown文件已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成ProductHunt Markdown文件失败: {e}")
            return ""
    
    def _generate_github_markdown_content(self, repositories: List[Dict], date: datetime) -> str:
        """生成GitHub Markdown内容"""
        date_str = date.strftime('%Y年%m月%d日')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 生成头部
        content = [
            "---",
            f"title: GitHub 每日趋势 - {date_str}",
            f"description: GitHub {date_str} 热门项目趋势",
            f"date: {date.strftime('%Y-%m-%d')}",
            "tags:",
            "  - github",
            "  - trending",
            f"  - {date.strftime('%Y')}",
            f"  - {date.strftime('%m')}",
            "---",
            "",
            f"# GitHub 每日趋势 - {date_str}",
            "",
        ]
        
        # 生成项目列表
        for i, repo in enumerate(repositories, 1):
            content.append(self._generate_repository_section(repo, i))
        
        # 添加统计信息
        content.extend([
            "## 📈 统计信息",
            "",
            "| 指标 | 数值 |",
            "|------|------|",
            f"| 总项目数 | {len(repositories)} |",
            f"| 主要语言 | {self._get_top_languages(repositories)} |",
            "",
            "## 🔗 相关链接",
            "",
            "- [GitHub Trending](https://github.com/trending) - 官方趋势页面",
            "- [历史记录](../) - 查看历史趋势",
            "",
            "---",
            "",
            "*本页面由自动化工具生成，每日更新*"
        ])
        
        return "\n".join(content)
    
    def _generate_producthunt_markdown_content(self, products: List[Dict], date: datetime) -> str:
        """生成ProductHunt Markdown内容"""
        date_str = date.strftime('%Y年%m月%d日')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 生成头部
        content = [
            "---",
            f"title: ProductHunt 每日热门 - {date_str}",
            f"description: ProductHunt {date_str} 热门产品",
            f"date: {date.strftime('%Y-%m-%d')}",
            "tags:",
            "  - producthunt",
            "  - products",
            f"  - {date.strftime('%Y')}",
            f"  - {date.strftime('%m')}",
            "---",
            "",
            f"# ProductHunt 每日热门 - {date_str}",
            "",
        ]
        
        # 生成产品列表
        for i, product in enumerate(products, 1):
            content.append(self._generate_product_section(product, i))
        
        # 添加统计信息
        content.extend([
            "## 📈 统计信息",
            "",
            "| 指标 | 数值 |",
            "|------|------|",
            f"| 总产品数 | {len(products)} |",
            f"| 平均投票数 | {self._calculate_average_votes(products):.0f} |",
            "",
            "## 🔗 相关链接",
            "",
            "- [ProductHunt](https://www.producthunt.com) - 官方产品页面",
            "- [历史记录](../) - 查看历史记录",
            "",
            "---",
            "",
            "*本页面由自动化工具生成，每日更新*"
        ])
        
        return "\n".join(content)
    
    def _generate_repository_section(self, repo: Dict, index: int) -> str:
        """生成单个仓库的Markdown部分"""
        stars_str = self._format_number(repo.get('stars', 0))
        forks_str = self._format_number(repo.get('forks', 0))
        today_stars_str = self._format_number(repo.get('today_stars', 0))
        
        # 生成标签字符串
        topics_str = ""
        if repo.get('topics'):
            topics_str = " ".join([f"`{topic}`" for topic in repo['topics']])
        
        # 生成语言徽章
        language = repo.get('language', 'Unknown')
        language_badge = f"![{language}](https://img.shields.io/badge/-{language}-3776AB?style=flat&logo={language.lower()}&logoColor=white)"
        
        # 生成仓库部分
        section = [
            f"## {index}. {repo['name']}",
            "",
            f"🔗 **项目地址**: [{repo['name']}]({repo['url']})",
            "",
            f"星标数: {stars_str} | Fork数: {forks_str} | 语言: {language}",
            "",
            "**英文描述**:",
            f"> {repo.get('description', '暂无描述')}",
            "",
            "**中文翻译**:",
            f"> {repo.get('description_zh', '暂无中文翻译')}",
            ""
        ]
        
        # 添加标签
        if topics_str:
            section.extend([
                "### 🏷️ 标签",
                "",
                topics_str,
                ""
            ])
        
        section.append("---")
        section.append("")
        
        return "\n".join(section)
    
    def _generate_product_section(self, product: Dict, index: int) -> str:
        """生成单个产品的Markdown部分"""
        votes_str = self._format_number(product.get('votes', 0))
        
        # 生成标签字符串
        tags_str = ""
        if product.get('tags'):
            tags_str = " ".join([f"`{tag}`" for tag in product['tags']])
        
        # 生成产品部分
        section = [
            f"## {index}. {product['name']}",
            "",
            f"🔗 **产品地址**: [{product['name']}]({product['url']})",
            "",
            f"投票数: {votes_str}",
            "",
            "**英文描述**:",
            f"> {product.get('description', '暂无描述')}",
            "",
            "**中文翻译**:",
            f"> {product.get('description_zh', '暂无中文翻译')}",
            ""
        ]
        
        # 添加标签
        if tags_str:
            section.extend([
                "### 🏷️ 标签",
                "",
                tags_str,
                ""
            ])
        
        section.append("---")
        section.append("")
        
        return "\n".join(section)
    
    def generate_today_file(self, github_repos: List[Dict], producthunt_products: List[Dict], date: datetime):
        """生成今日热门文件（用于主页）"""
        today_file = os.path.join(self.output_dir, "index.md")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = [
            "---",
            "title: 今日热门",
            "description: 今日GitHub热门项目和ProductHunt热门产品",
            f"date: {date.strftime('%Y-%m-%d')}",
            "---",
            "",
            f"# 今日热门 - {date.strftime('%Y年%m月%d日')}",
            "",
            f"> 最新更新: {current_time}",
            "",
            "## 🚀 GitHub 热门项目 (前5个)",
            ""
        ]
        
        # 添加前5个GitHub项目的简要信息
        for i, repo in enumerate(github_repos[:5], 1):
            desc = repo.get('description_zh', repo.get('description', '暂无描述'))
            content.append(f"{i}. **{repo['name']}** - {desc[:200]}...")
        
        content.extend([
            "",
            "## 🎯 ProductHunt 热门产品 (前5个)",
            ""
        ])
        
        # 添加前5个ProductHunt产品的简要信息
        for i, product in enumerate(producthunt_products[:5], 1):
            desc = product.get('description_zh', product.get('description', '暂无描述'))
            content.append(f"{i}. **{product['name']}** - {desc[:200]}...")
        
        content.extend([
            "",
            "## 📊 今日统计",
            "",
            f"- **GitHub项目**: {len(github_repos)} 个",
            f"- **ProductHunt产品**: {len(producthunt_products)} 个",
            "",
            "## 🔗 查看详情",
            "",
            f"👉 [GitHub完整列表](./github-trending-{date.strftime('%Y-%m-%d')}.md)",
            f"👉 [ProductHunt完整列表](./producthunt-{date.strftime('%Y-%m-%d')}.md)",
            "",
            "---",
            f"*自动更新于 {current_time}*"
        ])
        
        try:
            with open(today_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            logger.info(f"首页文件已生成: {today_file}")
        except Exception as e:
            logger.error(f"生成首页文件失败: {e}")
    
    def generate_github_history_page(self):
        """生成GitHub历史记录页面"""
        history_file = os.path.join(self.output_dir, "github-history.md")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取所有GitHub历史文件
        pattern = os.path.join(self.output_dir, "github-trending-*.md")
        files = glob.glob(pattern)
        files.sort(reverse=True)  # 按日期倒序
        
        content = [
            "---",
            "title: GitHub 历史记录",
            "description: GitHub 每日热门项目历史记录",
            "---",
            "",
            "# GitHub 历史记录",
            "",
            "> GitHub 每日热门项目的历史记录，按日期倒序排列",
            "",
            "## 📅 历史记录",
            ""
        ]
        
        # 按年份和月份分组显示
        year_month_groups = {}
        for file in files:
            filename = os.path.basename(file)
            date_str = filename.replace("github-trending-", "").replace(".md", "")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                year_month = date_obj.strftime("%Y年%m月")
                if year_month not in year_month_groups:
                    year_month_groups[year_month] = []
                year_month_groups[year_month].append((date_obj, filename))
            except:
                continue
        
        # 按年月倒序排列
        sorted_months = sorted(year_month_groups.keys(), reverse=True)
        
        for month in sorted_months:
            content.append(f"### {month}")
            content.append("")
            
            # 该月内的文件按日期倒序
            files_in_month = sorted(year_month_groups[month], key=lambda x: x[0], reverse=True)
            
            for date_obj, filename in files_in_month:
                formatted_date = date_obj.strftime("%m月%d日")
                content.append(f"- [{formatted_date}](./{filename})")
            
            content.append("")
        
        content.extend([
            "## 📊 统计信息",
            "",
            f"- **总记录数**: {len(files)} 条",
            f"- **时间跨度**: {self._get_date_range(files)}",
            "- **数据来源**: [GitHub Trending](https://github.com/trending)",
            "- **更新频率**: 每日自动更新",
            "",
            "## 🔗 快速导航",
            "",
            "### 最近一周",
            ""
        ])
        
        # 添加最近一周的快速链接
        recent_files = files[:7]  # 最近7个文件
        for file in recent_files:
            filename = os.path.basename(file)
            date_str = filename.replace("github-trending-", "").replace(".md", "")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%m月%d日")
                content.append(f"- [{formatted_date}](./{filename})")
            except:
                continue
        
        content.extend([
            "",
            "---",
            f"*最后更新: {current_time}*"
        ])
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            logger.info(f"GitHub历史记录页面已生成: {history_file}")
        except Exception as e:
            logger.error(f"生成GitHub历史记录页面失败: {e}")
    
    def generate_producthunt_history_page(self):
        """生成ProductHunt历史记录页面"""
        history_file = os.path.join(self.output_dir, "producthunt-history.md")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取所有ProductHunt历史文件
        pattern = os.path.join(self.output_dir, "producthunt-*.md")
        files = glob.glob(pattern)
        files.sort(reverse=True)  # 按日期倒序
        
        content = [
            "---",
            "title: ProductHunt 历史记录",
            "description: ProductHunt 每日热门产品历史记录",
            "---",
            "",
            "# ProductHunt 历史记录",
            "",
            "> ProductHunt 每日热门产品的历史记录，按日期倒序排列",
            "",
            "## 📅 历史记录",
            ""
        ]
        
        # 按年份和月份分组显示
        year_month_groups = {}
        for file in files:
            filename = os.path.basename(file)
            date_str = filename.replace("producthunt-", "").replace(".md", "")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                year_month = date_obj.strftime("%Y年%m月")
                if year_month not in year_month_groups:
                    year_month_groups[year_month] = []
                year_month_groups[year_month].append((date_obj, filename))
            except:
                continue
        
        # 按年月倒序排列
        sorted_months = sorted(year_month_groups.keys(), reverse=True)
        
        for month in sorted_months:
            content.append(f"### {month}")
            content.append("")
            
            # 该月内的文件按日期倒序
            files_in_month = sorted(year_month_groups[month], key=lambda x: x[0], reverse=True)
            
            for date_obj, filename in files_in_month:
                formatted_date = date_obj.strftime("%m月%d日")
                content.append(f"- [{formatted_date}](./{filename})")
            
            content.append("")
        
        content.extend([
            "## 📊 统计信息",
            "",
            f"- **总记录数**: {len(files)} 条",
            f"- **时间跨度**: {self._get_date_range(files)}",
            "- **数据来源**: [ProductHunt](https://www.producthunt.com)",
            "- **更新频率**: 每日自动更新",
            "",
            "## 🔗 快速导航",
            "",
            "### 最近一周",
            ""
        ])
        
        # 添加最近一周的快速链接
        recent_files = files[:7]  # 最近7个文件
        for file in recent_files:
            filename = os.path.basename(file)
            date_str = filename.replace("producthunt-", "").replace(".md", "")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%m月%d日")
                content.append(f"- [{formatted_date}](./{filename})")
            except:
                continue
        
        content.extend([
            "",
            "---",
            f"*最后更新: {current_time}*"
        ])
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            logger.info(f"ProductHunt历史记录页面已生成: {history_file}")
        except Exception as e:
            logger.error(f"生成ProductHunt历史记录页面失败: {e}")
    
    def _format_number(self, num: int) -> str:
        """格式化数字显示"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(num)
    
    def _calculate_average_stars(self, repositories: List[Dict]) -> float:
        """计算平均星标数"""
        if not repositories:
            return 0
        total_stars = sum(repo.get('stars', 0) for repo in repositories)
        return total_stars / len(repositories)
    
    def _calculate_average_forks(self, repositories: List[Dict]) -> float:
        """计算平均Fork数"""
        if not repositories:
            return 0
        total_forks = sum(repo.get('forks', 0) for repo in repositories)
        return total_forks / len(repositories)
    
    def _calculate_average_votes(self, products: List[Dict]) -> float:
        """计算平均投票数"""
        if not products:
            return 0
        total_votes = sum(product.get('votes', 0) for product in products)
        return total_votes / len(products)
    
    def _get_top_languages(self, repositories: List[Dict]) -> str:
        """获取主要编程语言"""
        languages = {}
        for repo in repositories:
            lang = repo.get('language', 'Unknown')
            languages[lang] = languages.get(lang, 0) + 1
        
        # 按数量排序，取前3个
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        top_langs = [lang for lang, count in sorted_langs[:3]]
        
        return ", ".join(top_langs)
    
    def _get_date_range(self, files: List[str]) -> str:
        """获取文件列表的时间跨度"""
        if not files:
            return "无数据"
        
        dates = []
        for file in files:
            filename = os.path.basename(file)
            if "github-trending-" in filename:
                date_str = filename.replace("github-trending-", "").replace(".md", "")
            elif "producthunt-" in filename:
                date_str = filename.replace("producthunt-", "").replace(".md", "")
            else:
                continue
            
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date_obj)
            except:
                continue
        
        if not dates:
            return "无数据"
        
        min_date = min(dates)
        max_date = max(dates)
        
        if min_date == max_date:
            return min_date.strftime("%Y年%m月%d日")
        else:
            return f"{min_date.strftime('%Y年%m月%d日')} - {max_date.strftime('%Y年%m月%d日')}"
    
    def generate_summary_file(self, repositories: List[Dict], date: datetime = None) -> str:
        """生成汇总文件"""
        if date is None:
            date = datetime.now()
        
        filename = "README.md"
        filepath = os.path.join(self.output_dir, filename)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = [
            "# GitHub 每日趋势汇总",
            "",
            "> 这是一个自动生成的GitHub每日趋势项目汇总，每日更新最新的热门开源项目。",
            "",
            "## 📅 最新更新",
            "",
            f"**更新时间**: {date.strftime('%Y年%m月%d日')}",
            "",
            f"**今日收录项目**: {len(repositories)} 个",
            "",
            "## 🚀 今日热门项目",
            ""
        ]
        
        # 添加前10个项目的简要信息
        for i, repo in enumerate(repositories[:10], 1):
            desc = repo.get('description_zh', repo.get('description', '暂无描述'))
            content.append(f"{i}. **{repo['name']}** - {desc[:100]}...")
        
        content.extend([
            "",
            "## 📁 历史记录",
            "",
            f"- [{date.strftime('%Y年%m月%d日')}](./trending-{date.strftime('%Y-%m-%d')}.md) - {len(repositories)} 个项目",
            "",
            "## 🔧 技术栈",
            "",
            "- **数据抓取**: Python + BeautifulSoup",
            "- **翻译服务**: DeepSeek AI API",
            "- **文档生成**: Markdown",
            "- **自动化**: 定时任务",
            "",
            "## 📝 说明",
            "",
            "本项目自动抓取GitHub Trending页面，使用AI翻译项目描述，并生成结构化的Markdown文档。",
            "",
            "---",
            f"*最后更新: {current_time}*"
        ])
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            
            logger.info(f"汇总文件已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成汇总文件失败: {e}")
            return ""

