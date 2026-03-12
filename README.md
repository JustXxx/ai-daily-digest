# AI Daily Digest

从 90 个 Hacker News 顶级技术博客中抓取最新文章，通过 AI 多维评分筛选，生成一份结构化的每日精选日报。默认使用 Gemini，并支持自动降级到 OpenAI 兼容 API。

> 信息源来自 [Hacker News Popularity Contest 2025](https://refactoringenglish.com/tools/hn-popularity/)，涵盖 simonwillison.net、paulgraham.com、overreacted.io、gwern.net、krebsonsecurity.com 等。

## 使用方式

作为 CodeBuddy Skill 使用，在对话中输入 `/digest` 即可启动交互式引导流程：

```
/digest
```

Agent 会依次询问：

| 参数 | 选项 | 默认值 |
|------|------|--------|
| 时间范围 | 24h / 48h / 72h / 7天 | 48h |
| 精选数量 | 10 / 15 / 20 篇 | 15 篇 |
| 输出语言 | 中文 / English | 中文 |
| Gemini API Key | 环境变量传入（首次需提供） | — |

配置（时间范围、精选数量、语言）自动保存到 `~/.hn-daily-digest/config.json`，下次运行可一键复用。API Key 通过环境变量传递，不存入配置文件。

### 直接命令行运行

```bash
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-openai-compatible-key"  # 可选，Gemini 失败时兜底
export OPENAI_API_BASE="https://api.deepseek.com/v1" # 可选，默认 https://api.openai.com/v1
export OPENAI_MODEL="deepseek-chat"                  # 可选，不填会自动推断

pip install requests
python scripts/digest.py --hours 48 --top-n 15 --lang zh --output ./digest.md
```

## 功能

### 五步处理流水线

```
RSS 抓取 → 时间过滤 → AI 评分+分类 → AI 摘要+翻译 → 趋势总结
```

1. **RSS 抓取** — 并发抓取 90 个源（10 路并发，15s 超时），兼容 RSS 2.0 和 Atom 格式
2. **时间过滤** — 按指定时间窗口筛选近期文章
3. **AI 评分** — AI 从相关性、质量、时效性三个维度打分（1-10），同时完成分类和关键词提取（Gemini 优先，失败自动降级到 OpenAI 兼容接口）
4. **AI 摘要** — 为 Top N 文章生成结构化摘要（4-6 句）、中文标题翻译、推荐理由
5. **趋势总结** — AI 归纳当日技术圈 2-3 个宏观趋势

### 日报结构

生成的 Markdown 文件包含以下板块：

| 板块 | 内容 |
|------|------|
| 📝 今日看点 | 3-5 句话的宏观趋势总结 |
| 🏆 今日必读 | Top 3 深度展示：中英双语标题、摘要、推荐理由、关键词 |
| 📊 数据概览 | 统计表格 + Mermaid 饼图（分类分布）+ Mermaid 柱状图（高频关键词）+ ASCII 纯文本图 + 话题标签云 |
| 分类文章列表 | 按 6 大分类分组，每篇含中文标题、来源、相对时间、评分、摘要、关键词 |

### 六大分类体系

| 分类 | 覆盖范围 |
|------|----------|
| 🤖 AI / ML | AI、机器学习、LLM、深度学习 |
| 🔒 安全 | 安全、隐私、漏洞、加密 |
| ⚙️ 工程 | 软件工程、架构、编程语言、系统设计 |
| 🛠 工具 / 开源 | 开发工具、开源项目、新发布的库/框架 |
| 💡 观点 / 杂谈 | 行业观点、个人思考、职业发展 |
| 📝 其他 | 不属于以上分类的内容 |

## 亮点

- **轻量依赖** — Python 单依赖（`requests`），无重型框架
- **模块化架构** — 入口、抓取、AI、报告、prompt 模板各司其职，清晰可维护
- **中英双语** — 所有标题自动翻译为中文，原文标题保留为链接文字
- **结构化摘要** — 4-6 句覆盖核心问题→关键论点→结论的完整概述，30 秒判断一篇文章是否值得读
- **可视化统计** — Mermaid 图表（GitHub/Obsidian 原生渲染）+ ASCII 柱状图（终端友好）+ 标签云
- **智能分类** — AI 自动将文章归入 6 大类别，按类浏览比平铺列表高效得多
- **趋势洞察** — 不只是文章列表，还会归纳当天技术圈的宏观趋势
- **双 AI 通道** — Gemini 优先，失败自动降级到 OpenAI 兼容接口，零人工干预

## 环境要求

- Python 3.9+
- `requests` 库（`pip install requests`）
- 至少一个可用的 AI API Key：
  - `GEMINI_API_KEY`（[免费获取](https://aistudio.google.com/apikey)）
  - 或 `OPENAI_API_KEY`（可配合 `OPENAI_API_BASE` 使用 DeepSeek / OpenAI 等兼容服务）
- 网络连接

## 项目结构

```
scripts/
├── digest.py         # CLI 入口，参数解析与流程编排
├── constants.py      # RSS 源列表、分类元数据、全局常量
├── models.py         # Article / ScoredArticle 数据类
├── feeds.py          # RSS/Atom XML 解析与并发抓取
├── ai.py             # Gemini/OpenAI 双通道 AI 客户端
├── report.py         # Mermaid 图表与 Markdown 日报生成
└── prompts/          # AI prompt 模板（评分/摘要/看点）
    ├── scoring.txt
    ├── summary_zh.txt
    ├── summary_en.txt
    ├── highlights_zh.txt
    └── highlights_en.txt
```

## 切换 AI 模型提供商

本项目默认使用 Gemini API（免费）。如需替换为其他提供商，修改 `scripts/ai.py` 中的 API 调用逻辑即可：

| 位置 | 说明 |
|------|------|
| `GEMINI_API_URL` 常量（`constants.py`） | API endpoint 地址 |
| `_call_gemini()` 函数（`ai.py`） | 请求构造 + 响应解析，约 25 行 |

Prompt 模板（`prompts/*.txt`）与 AI 提供商无关，切换模型后可直接复用。

### 常见替换示例

| 提供商 | API Endpoint | Key 环境变量 |
|--------|-------------|-------------|
| OpenAI | `https://api.openai.com/v1/chat/completions` | `OPENAI_API_KEY` |
| Anthropic | `https://api.anthropic.com/v1/messages` | `ANTHROPIC_API_KEY` |
| DeepSeek | `https://api.deepseek.com/v1/chat/completions` | `DEEPSEEK_API_KEY` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` | `DASHSCOPE_API_KEY` |

> 💡 如果目标提供商兼容 OpenAI API 格式（如 DeepSeek、Groq、Together AI 等），只需设置 `OPENAI_API_BASE` 和 `OPENAI_API_KEY` 环境变量即可，无需改代码。

## 信息源

90 个 RSS 源精选自 Hacker News 社区最受欢迎的独立技术博客，包括但不限于：

> Simon Willison · Paul Graham · Dan Abramov · Gwern · Krebs on Security · Antirez · John Gruber · Troy Hunt · Mitchell Hashimoto · Steve Blank · Eli Bendersky · Fabien Sanglard ...

完整列表见 `scripts/constants.py`。
