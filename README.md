# DayHot - 每日热门项目与产品聚合

一个自动化的工具，每日抓取 GitHub 热门项目和 ProductHunt 热门产品，翻译描述并生成静态网站。

## 🌟 功能特性

- **GitHub 热门项目抓取**: 自动抓取 GitHub Trending 页面的热门开源项目
- **ProductHunt 热门产品抓取**: 自动抓取 ProductHunt 页面的热门产品
- **AI 翻译**: 使用 DeepSeek AI 将项目描述翻译成中文
- **自动生成文档**: 生成结构化的 Markdown 文档
- **静态网站**: 使用 MkDocs 构建美观的静态网站
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
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 3. 运行程序

```bash
python main.py
```

### 4. 构建网站

```bash
python build_site.py build
```

### 5. 启动开发服务器

```bash
python build_site.py serve
```

## 📊 输出文件

程序运行后会在 `mkdocs/daily-trending/` 目录下生成以下文件：

- `trending-today.md` - 今日热门（主页）
- `github-trending-YYYY-MM-DD.md` - GitHub 每日详细列表
- `producthunt-YYYY-MM-DD.md` - ProductHunt 每日详细列表

## 🔧 配置说明

### 环境变量

- `DEEPSEEK_API_KEY`: DeepSeek AI API 密钥（必需）
- `DEEPSEEK_BASE_URL`: DeepSeek API 基础 URL（可选，默认为 https://api.deepseek.com）

### 输出目录

- 默认输出目录: `./mkdocs/daily-trending/`
- 网站构建目录: `./site/`

## 📅 定时任务

可以使用 `scheduler.py` 设置定时任务：

```bash
python scheduler.py
```

支持以下定时选项：
- 每日凌晨 2 点自动运行
- 可自定义运行时间
- 支持多种编程语言筛选

## 🌐 网站功能

生成的静态网站包含：

- **主页**: 显示今日 GitHub 前 5 个热门项目和 ProductHunt 前 5 个热门产品
- **GitHub 历史记录**: 查看历史 GitHub 热门项目
- **ProductHunt 历史记录**: 查看历史 ProductHunt 热门产品

## 🛠️ 技术栈

- **Python 3.8+**: 主要编程语言
- **BeautifulSoup4**: 网页解析
- **Requests**: HTTP 请求
- **DeepSeek AI**: 文本翻译
- **MkDocs**: 静态网站生成
- **Material for MkDocs**: 网站主题

## 📝 使用示例

### 抓取特定语言的项目

```python
from main import DayHotTool

tool = DayHotTool()
# 抓取 Python 项目
tool.run_once(language="python", since="daily")
```

### 自定义时间范围

```python
# 抓取本周热门项目
tool.run_once(language="any", since="weekly")
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [GitHub Trending](https://github.com/trending) - GitHub 热门项目
- [ProductHunt](https://www.producthunt.com) - 产品发现平台
- [DeepSeek AI](https://www.deepseek.com) - AI 翻译服务
- [MkDocs](https://www.mkdocs.org) - 静态网站生成器

---

*本项目仅供学习和研究使用，请遵守相关网站的使用条款。*

