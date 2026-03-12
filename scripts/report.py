# -*- coding: utf-8 -*-
"""可视化辅助工具与 Markdown 日报生成。"""

from collections import Counter
from datetime import datetime
from datetime import timezone
from typing import Dict
from typing import List

from .constants import CATEGORY_META
from .models import ScoredArticle

# ============================================================================
# Visualization Helpers
# ============================================================================


def _humanize_time(pub_date: datetime) -> str:
    """生成相对时间字符串。"""
    now = datetime.now(timezone.utc)
    diff = now - pub_date
    diff_mins = int(diff.total_seconds() / 60)
    diff_hours = int(diff.total_seconds() / 3600)
    diff_days = int(diff.total_seconds() / 86400)

    if diff_mins < 60:
        return f"{diff_mins} 分钟前"
    if diff_hours < 24:
        return f"{diff_hours} 小时前"
    if diff_days < 7:
        return f"{diff_days} 天前"
    return pub_date.strftime("%Y-%m-%d")


def _keyword_counter(articles: List[ScoredArticle]) -> Counter:
    counter: Counter = Counter()
    for a in articles:
        for kw in a.keywords:
            counter[kw.lower()] += 1
    return counter


def _gen_mermaid_pie(articles: List[ScoredArticle]) -> str:
    cat_count: Counter = Counter()
    for a in articles:
        cat_count[a.category] += 1

    if not cat_count:
        return ""

    lines = ['```mermaid', 'pie showData', '    title "文章分类分布"']
    for cat, count in cat_count.most_common():
        meta = CATEGORY_META.get(cat, {"emoji": "📝", "label": cat})
        lines.append(f'    "{meta["emoji"]} {meta["label"]}" : {count}')
    lines.append("```")
    return "\n".join(lines) + "\n"


def _gen_mermaid_bar(articles: List[ScoredArticle]) -> str:
    kw = _keyword_counter(articles).most_common(12)
    if not kw:
        return ""

    labels = ", ".join(f'"{k}"' for k, __ in kw)
    values = ", ".join(str(v) for __, v in kw)
    max_val = kw[0][1]

    lines = [
        "```mermaid",
        "xychart-beta horizontal",
        '    title "高频关键词"',
        f"    x-axis [{labels}]",
        f'    y-axis "出现次数" 0 --> {max_val + 2}',
        f"    bar [{values}]",
        "```",
    ]
    return "\n".join(lines) + "\n"


def _gen_ascii_bar(articles: List[ScoredArticle]) -> str:
    kw = _keyword_counter(articles).most_common(10)
    if not kw:
        return ""

    max_val = kw[0][1]
    max_bar = 20
    max_label = max(len(k) for k, __ in kw)

    lines = ["```"]
    for label, value in kw:
        bar_len = max(1, round((value / max_val) * max_bar))
        bar = "█" * bar_len + "░" * (max_bar - bar_len)
        lines.append(f"{label:<{max_label}} │ {bar} {value}")
    lines.append("```")
    return "\n".join(lines) + "\n"


def _gen_tag_cloud(articles: List[ScoredArticle]) -> str:
    kw = _keyword_counter(articles).most_common(20)
    if not kw:
        return ""

    parts = []
    for i, (word, count) in enumerate(kw):
        if i < 3:
            parts.append(f"**{word}**({count})")
        else:
            parts.append(f"{word}({count})")
    return " · ".join(parts)


# ============================================================================
# Report Generation
# ============================================================================

def generate_report(
    articles: List[ScoredArticle],
    highlights: str,
    total_feeds: int,
    success_feeds: int,
    total_articles: int,
    filtered_articles: int,
    hours: int,
) -> str:
    """生成最终的 Markdown 日报。"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    lines: List[str] = []
    w = lines.append

    w(f"# 📰 AI 博客每日精选 — {date_str}\n")
    w(f"> 来自 {total_feeds} 个顶级技术博客，AI 精选 Top {len(articles)}\n")

    # 今日看点
    if highlights:
        w("## 📝 今日看点\n")
        w(f"{highlights}\n")
        w("---\n")

    # Top 3
    if len(articles) >= 3:
        w("## 🏆 今日必读\n")
        medals = ["🥇", "🥈", "🥉"]
        for i in range(min(3, len(articles))):
            a = articles[i]
            meta = CATEGORY_META.get(a.category, {"emoji": "📝", "label": a.category})
            w(f"{medals[i]} **{a.title_zh or a.title}**\n")
            w(f"[{a.title}]({a.link}) — {a.source_name} · {_humanize_time(a.pub_date)} · {meta['emoji']} {meta['label']}\n")
            w(f"> {a.summary}\n")
            if a.reason:
                w(f"💡 **为什么值得读**: {a.reason}\n")
            if a.keywords:
                w(f"🏷️ {', '.join(a.keywords)}\n")
        w("---\n")

    # 数据概览
    w("## 📊 数据概览\n")
    w("| 扫描源 | 抓取文章 | 时间范围 | 精选 |")
    w("|:---:|:---:|:---:|:---:|")
    w(f"| {success_feeds}/{total_feeds} | {total_articles} 篇 → {filtered_articles} 篇 | {hours}h | **{len(articles)} 篇** |\n")

    pie = _gen_mermaid_pie(articles)
    if pie:
        w(f"### 分类分布\n\n{pie}")

    bar = _gen_mermaid_bar(articles)
    if bar:
        w(f"### 高频关键词\n\n{bar}")

    ascii_bar = _gen_ascii_bar(articles)
    if ascii_bar:
        w(f"<details>\n<summary>📈 纯文本关键词图（终端友好）</summary>\n\n{ascii_bar}\n</details>\n")

    tag_cloud = _gen_tag_cloud(articles)
    if tag_cloud:
        w(f"### 🏷️ 话题标签\n\n{tag_cloud}\n")

    w("---\n")

    # 分类列表
    cat_groups: Dict[str, List[ScoredArticle]] = {}
    for a in articles:
        cat_groups.setdefault(a.category, []).append(a)

    sorted_cats = sorted(cat_groups.items(), key=lambda x: len(x[1]), reverse=True)

    global_idx = 0
    for cat_id, cat_articles in sorted_cats:
        meta = CATEGORY_META.get(cat_id, {"emoji": "📝", "label": cat_id})
        w(f"## {meta['emoji']} {meta['label']}\n")

        for a in cat_articles:
            global_idx += 1
            total = a.score_breakdown.relevance + a.score_breakdown.quality + a.score_breakdown.timeliness
            w(f"### {global_idx}. {a.title_zh or a.title}\n")
            w(f"[{a.title}]({a.link}) — **{a.source_name}** · {_humanize_time(a.pub_date)} · ⭐ {total}/30\n")
            w(f"> {a.summary}\n")
            if a.keywords:
                w(f"🏷️ {', '.join(a.keywords)}\n")
            w("---\n")

    # Footer
    time_str = now.strftime("%H:%M")
    w(f"*生成于 {date_str} {time_str} | 扫描 {success_feeds} 源 → 获取 {total_articles} 篇 → 精选 {len(articles)} 篇*")
    w("*基于 [Hacker News Popularity Contest 2025](https://refactoringenglish.com/tools/hn-popularity/) RSS 源列表*")

    return "\n".join(lines) + "\n"
