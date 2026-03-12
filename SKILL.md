---
name: ai-daily-digest
description: "This skill should be used when a user mentions 'daily digest', 'RSS digest', 'blog digest', 'AI blogs', 'tech news summary', or requests the /digest command. It fetches RSS feeds from 90 top Hacker News tech blogs, scores and filters articles with AI (Gemini/OpenAI), and generates a structured daily Markdown digest with translated titles, category grouping, trend highlights, and visual statistics. Trigger command: /digest."
---

# AI Daily Digest

从 90 个顶级技术博客抓取最新文章，通过 AI 多维评分筛选，生成结构化每日精选日报。

## 触发命令

`/digest` — 启动每日摘要生成流程。

---

## 脚本

所有脚本位于 `scripts/` 子目录。确定此 SKILL.md 所在目录为 `SKILL_DIR`，脚本路径为 `${SKILL_DIR}/scripts/digest.py`。

入口脚本为 `scripts/digest.py`，内部模块（`constants.py`、`models.py`、`feeds.py`、`ai.py`、`report.py`）和 prompt 模板（`prompts/*.txt`）由入口脚本自动加载，无需单独调用。

---

## 执行流程

### Step 0: 检查已保存配置

```bash
cat ~/.hn-daily-digest/config.json 2>/dev/null || echo "NO_CONFIG"
```

若配置存在，向用户展示已保存参数（时间范围、精选数量、语言），询问是否复用或重新配置。

### Step 1: 收集参数

若需重新配置或无已保存配置，通过交互收集以下参数：

| 参数 | 选项 | 脚本参数 |
|------|------|----------|
| 时间范围 | 24h / **48h** (推荐) / 72h / 7天 | `--hours 24\|48\|72\|168` |
| 精选数量 | 10篇 / **15篇** (推荐) / 20篇 | `--top-n 10\|15\|20` |
| 输出语言 | **中文** (推荐) / English | `--lang zh\|en` |

### Step 1b: AI API Key

若环境变量中无 `GEMINI_API_KEY` 且无 `OPENAI_API_KEY`，提示用户提供至少一个：

- **Gemini（推荐主模型）**: 免费获取 https://aistudio.google.com/apikey
- **OpenAI 兼容接口（可选兜底）**: 支持 DeepSeek、OpenAI 等

API Key 通过环境变量传递，不存入配置文件。

### Step 2: 执行脚本

```bash
mkdir -p ./output

export GEMINI_API_KEY="<key>"
# 可选：OpenAI 兼容兜底
export OPENAI_API_KEY="<fallback-key>"
export OPENAI_API_BASE="https://api.deepseek.com/v1"
export OPENAI_MODEL="deepseek-chat"

pip install -q requests 2>/dev/null

python ${SKILL_DIR}/scripts/digest.py \
  --hours <timeRange> \
  --top-n <topN> \
  --lang <zh|en> \
  --output ./output/digest-$(date +%Y%m%d).md
```

### Step 2b: 保存配置

仅保存非敏感参数，API Key 不入配置：

```bash
mkdir -p ~/.hn-daily-digest
cat > ~/.hn-daily-digest/config.json << EOF
{
  "timeRange": <hours>,
  "topN": <topN>,
  "language": "<zh|en>",
  "lastUsed": "<ISO timestamp>"
}
EOF
```

### Step 3: 结果展示

**成功时**：
- 📁 报告文件路径
- 📊 扫描源数 → 抓取文章数 → 精选文章数
- 🏆 Top 3 预览：中文标题 + 一句话摘要

**报告结构**（生成的 Markdown 文件）：
1. **今日看点** — AI 归纳的宏观趋势总结
2. **今日必读 Top 3** — 双语标题、摘要、推荐理由、关键词
3. **数据概览** — 统计表 + Mermaid 图表 + 标签云
4. **分类列表** — 按 6 大分类分组（AI/ML、安全、工程、工具/开源、观点/杂谈、其他）

**失败时**：显示错误信息，参考 `references/troubleshooting.md` 排查。

---

## 环境要求

- Python 3.9+
- `requests` 库（`pip install requests`）
- 至少一个 AI API Key（`GEMINI_API_KEY` 或 `OPENAI_API_KEY`）
- 网络访问（RSS 源 + AI API）

---

## 信息源

90 个 RSS 源来自 [Hacker News Popularity Contest 2025](https://refactoringenglish.com/tools/hn-popularity/)，完整列表内嵌于 `scripts/constants.py`。
