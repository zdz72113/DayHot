# DayHot - 每日热门项目与产品聚合

一个自动化的工具，每日抓取 GitHub 热门项目、ProductHunt 热门产品和 Hacker News 热门新闻，翻译描述并生成静态网站。

## 🌟 功能特性

- **GitHub 热门项目抓取**: 自动抓取 GitHub Trending 页面的热门开源项目
- **ProductHunt 热门产品抓取**: 自动抓取 ProductHunt 页面的热门产品
- **Hacker News 热门新闻抓取**: 自动抓取 Hacker News 的热门技术新闻
- **AI 翻译**: 使用 DeepSeek AI 将项目描述和新闻内容翻译成中文
- **自动生成文档**: 生成结构化的 Markdown 文档
- **静态网站**: 使用 MkDocs 构建静态网站
- **每日更新**: 支持定时任务自动更新

## 📁 项目结构

```
DayHot/
├── main.py                 # 主程序入口
├── config.py              # 配置文件
├── build_site.py          # 网站构建脚本
├── scheduler.py           # 定时任务调度器
├── requirements.txt       # Python 依赖
├── mkdocs.yml            # MkDocs 配置
├── README.md             # 项目说明
└── scraper/              # 抓取器模块
    ├── __init__.py
    ├── github_scraper.py     # GitHub 抓取器
    ├── producthunt_scraper.py # ProductHunt 抓取器
    ├── hackernews_scraper.py # Hacker News 抓取器
    ├── translator.py          # 翻译器
    └── markdown_generator.py  # Markdown 生成器
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件并设置以下环境变量：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Product Hunt配置
PRODUCTHUNT_DEVELOPER_TOKEN=your_producthunt_developer_token_here
PRODUCTHUNT_CLIENT_ID=your_producthunt_api_key_here
PRODUCTHUNT_CLIENT_SECRET=your_producthunt_api_secret_here
```

### 3. 运行程序

单次运行

```bash
python main.py
```

使用 `scheduler.py` 设置定时任务：

```bash
python scheduler.py
```

## 🌐 网站功能

生成的静态网站包含：

- **主页**: 显示今日 GitHub 前 5 个热门项目、ProductHunt 前 5 个热门产品和 Hacker News 前 5 个热门新闻
- **GitHub 历史记录**: 查看历史 GitHub 热门项目
- **ProductHunt 历史记录**: 查看历史 ProductHunt 热门产品
- **Hacker News 历史记录**: 查看历史 Hacker News 热门新闻

## 🛠️ 技术栈

- **Python**: 主要编程语言
- **DeepSeek AI**: 文本翻译
- **MkDocs**: 静态网站生成

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [GitHub Trending](https://github.com/trending) - GitHub 热门项目
- [ProductHunt](https://www.producthunt.com) - 产品发现平台
- [Hacker News](https://news.ycombinator.com) - 技术新闻社区
- [DeepSeek AI](https://www.deepseek.com) - AI 翻译服务
- [MkDocs](https://www.mkdocs.org) - 静态网站生成器

---

*本项目仅供学习和研究使用，请遵守相关网站的使用条款。*

