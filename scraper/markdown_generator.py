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
        """生成每日trending的Markdown文件"""
        if date is None:
            date = datetime.now()
        
        filename = f"trending-{date.strftime('%Y-%m-%d')}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            content = self._generate_markdown_content(repositories, date)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 生成今日趋势文件
            self._generate_today_file(repositories, date)
            
            # 更新导航文件
            # self._update_navigation()
            
            logger.info(f"Markdown文件已生成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成Markdown文件失败: {e}")
            return ""
    
    def _generate_markdown_content(self, repositories: List[Dict], date: datetime) -> str:
        """生成Markdown内容"""
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
            # "> 自动抓取的GitHub热门项目趋势，每日更新",
            # "",
            # "## 📊 今日概览",
            # "",
            # f"- **收录项目**: {len(repositories)} 个",
            # f"- **更新时间**: {current_time}",
            # "- **数据来源**: [GitHub Trending](https://github.com/trending)",
            # "",
            # "---",
            # ""
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
            # f"| 平均星标数 | {self._calculate_average_stars(repositories):.0f} |",
            # f"| 平均Fork数 | {self._calculate_average_forks(repositories):.0f} |",
            f"| 主要语言 | {self._get_top_languages(repositories)} |",
            "",
            "## 🔗 相关链接",
            "",
            "- [GitHub Trending](https://github.com/trending) - 官方趋势页面",
            "- [历史记录](../) - 查看历史趋势",
            "- [项目源码](https://github.com/your-repo/github-daily-trending) - 本工具源码",
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
            # "<div class=\"repo-header\">",
            # "",
            # f"[![GitHub stars](https://img.shields.io/github/stars/{repo['name']}?style=social)]({repo['url']})",
            # f"[![GitHub forks](https://img.shields.io/github/forks/{repo['name']}?style=social)]({repo['url']}/network/members)",
            # language_badge,
            # "",
            # "</div>",
            # "",
            f"星标数: {stars_str} | Fork数: {forks_str} | 语言: {language}",
            "",
            # "### 📝 项目简介",
            # "",
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
    
    def _generate_today_file(self, repositories: List[Dict], date: datetime):
        """生成今日趋势文件（用于导航）"""
        today_file = os.path.join(self.output_dir, "trending-today.md")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = [
            "---",
            "title: 今日热门",
            "description: 今日GitHub热门项目",
            f"date: {date.strftime('%Y-%m-%d')}",
            "---",
            "",
            f"# 今日热门",
            "",
            # f"> 最新更新: {current_time}",
            # "",
            # "## 🚀 热门项目预览",
            # ""
        ]
        
        # 添加前5个项目的简要信息
        for i, repo in enumerate(repositories[:5], 1):
            desc = repo.get('description_zh', repo.get('description', '暂无描述'))
            content.append(f"{i}. **{repo['name']}** - {desc[:200]}...")
        
        content.extend([
            "",
            # "## 📊 今日统计",
            # "",
            # f"- **收录项目**: {len(repositories)} 个",
            # f"- **平均星标数**: {self._calculate_average_stars(repositories):.0f}",
            # f"- **主要语言**: {self._get_top_languages(repositories)}",
            # "",
            # "## 🔗 查看详情",
            # "",
            f"👉 [查看完整列表](./trending-{date.strftime('%Y-%m-%d')}.md)",
            "",
            "---",
            f"*自动更新于 {current_time}*"
        ])
        
        try:
            with open(today_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            logger.info(f"今日趋势文件已生成: {today_file}")
        except Exception as e:
            logger.error(f"生成今日趋势文件失败: {e}")
    
    def _update_navigation(self):
        """更新导航文件"""
        nav_file = os.path.join(self.output_dir, "index.md")
        
        # 获取所有历史文件
        pattern = os.path.join(self.output_dir, "trending-*.md")
        files = glob.glob(pattern)
        files.sort(reverse=True)  # 按日期倒序
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = [
            "---",
            "title: GitHub 每日趋势",
            "description: 自动抓取的GitHub热门项目趋势",
            "---",
            "",
            "# GitHub 每日趋势",
            "",
            "> 自动抓取的GitHub热门项目趋势，每日更新",
            "",
            "## 📅 最新更新",
            ""
        ]
        
        # 添加最近的文件链接
        for file in files[:10]:  # 只显示最近10个
            filename = os.path.basename(file)
            date_str = filename.replace("trending-", "").replace(".md", "")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%Y年%m月%d日")
                content.append(f"- [{formatted_date}](./{filename})")
            except:
                continue
        
        content.extend([
            "",
            "## 📊 项目统计",
            "",
            "- **数据来源**: [GitHub Trending](https://github.com/trending)",
            "- **更新频率**: 每日自动更新",
            "- **翻译服务**: DeepSeek AI",
            "",
            "## 🔧 技术栈",
            "",
            "- **数据抓取**: Python + BeautifulSoup",
            "- **翻译服务**: DeepSeek AI API",
            "- **文档生成**: Markdown",
            "- **网站构建**: MkDocs + Material主题",
            "- **自动化**: 定时任务 + GitHub Actions",
            "",
            "---",
            f"*最后更新: {current_time}*"
        ])
        
        try:
            with open(nav_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            logger.info(f"导航文件已更新: {nav_file}")
        except Exception as e:
            logger.error(f"更新导航文件失败: {e}")
    
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

