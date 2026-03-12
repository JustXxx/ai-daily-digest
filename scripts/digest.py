# -*- coding: utf-8 -*-
"""AI Daily Digest — Python 版。

从 90 个 Hacker News 顶级技术博客中抓取最新文章，
通过 AI 多维评分筛选，生成一份结构化的每日精选日报。

用法:
    python -m scripts.digest --hours 48 --top-n 15 --lang zh --output ./digest.md

环境变量:
    GEMINI_API_KEY   推荐。免费获取: https://aistudio.google.com/apikey
    OPENAI_API_KEY   可选兜底 (OpenAI 兼容接口)
    OPENAI_API_BASE  可选兜底 base URL (默认 https://api.openai.com/v1)
    OPENAI_MODEL     可选兜底 model (默认根据 base URL 推断)
"""

import argparse
import os
import sys
from datetime import datetime
from datetime import timezone
from pathlib import Path

# 支持 `python scripts/digest.py` 直接运行
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "scripts"

from .ai import AIClient
from .ai import generate_highlights
from .ai import score_articles
from .ai import summarize_articles
from .constants import OPENAI_DEFAULT_API_BASE
from .constants import RSS_FEEDS
from .feeds import fetch_all_feeds
from .models import ScoreBreakdown
from .models import ScoredArticle
from .report import generate_report


def main() -> None:
    """主入口。"""
    parser = argparse.ArgumentParser(
        description="AI Daily Digest - AI-powered RSS digest from 90 top tech blogs",
    )
    parser.add_argument("--hours", type=int, default=48, help="Time range in hours (default: 48)")
    parser.add_argument("--top-n", type=int, default=15, help="Number of top articles (default: 15)")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="Summary language (default: zh)")
    parser.add_argument("--output", type=str, default="", help="Output file path")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    openai_base = os.environ.get("OPENAI_API_BASE", "")
    openai_model = os.environ.get("OPENAI_MODEL", "")

    if not gemini_key and not openai_key:
        print("[digest] Error: Missing API key. Set GEMINI_API_KEY and/or OPENAI_API_KEY.", file=sys.stderr)
        print("[digest] Gemini key: https://aistudio.google.com/apikey", file=sys.stderr)
        sys.exit(1)

    ai_client = AIClient(
        gemini_api_key=gemini_key,
        openai_api_key=openai_key,
        openai_api_base=openai_base,
        openai_model=openai_model,
    )

    output_path = args.output
    if not output_path:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        output_path = f"./digest-{date_str}.md"

    print("[digest] === AI Daily Digest (Python) ===")
    print(f"[digest] Time range: {args.hours} hours")
    print(f"[digest] Top N: {args.top_n}")
    print(f"[digest] Language: {args.lang}")
    print(f"[digest] Output: {output_path}")
    provider = "Gemini (primary)" if gemini_key else "OpenAI-compatible (primary)"
    print(f"[digest] AI provider: {provider}")
    if openai_key:
        print(f"[digest] Fallback: {ai_client.openai_base} (model={ai_client.openai_model})")
    print()

    # Step 1: Fetch
    print(f"[digest] Step 1/5: Fetching {len(RSS_FEEDS)} RSS feeds...")
    all_articles, success_count, __ = fetch_all_feeds(RSS_FEEDS)

    if not all_articles:
        print("[digest] Error: No articles fetched from any feed. Check network connection.", file=sys.stderr)
        sys.exit(1)

    # Step 2: Filter by time
    print(f"[digest] Step 2/5: Filtering by time range ({args.hours} hours)...")
    cutoff = datetime.now(timezone.utc).timestamp() - args.hours * 3600
    recent = [a for a in all_articles if a.pub_date.timestamp() > cutoff]
    print(f"[digest] Found {len(recent)} articles within last {args.hours} hours")

    if not recent:
        print(f"[digest] Error: No articles found within the last {args.hours} hours.", file=sys.stderr)
        print("[digest] Try increasing --hours (e.g., --hours 168 for one week)", file=sys.stderr)
        sys.exit(1)

    # Step 3: AI Scoring
    print(f"[digest] Step 3/5: AI scoring {len(recent)} articles...")
    scores = score_articles(recent, ai_client)

    scored = []
    for i, article in enumerate(recent):
        s = scores.get(i, {"relevance": 5, "quality": 5, "timeliness": 5, "category": "other", "keywords": []})
        total = s["relevance"] + s["quality"] + s["timeliness"]
        scored.append((total, i, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_indices = [idx for __, idx, __ in scored[:args.top_n]]
    top_scores = {idx: s for __, idx, s in scored[:args.top_n]}

    score_range_lo = scored[min(args.top_n - 1, len(scored) - 1)][0] if scored else 0
    score_range_hi = scored[0][0] if scored else 0
    print(f"[digest] Top {args.top_n} articles selected (score range: {score_range_lo} - {score_range_hi})")

    # Step 4: AI Summaries
    print("[digest] Step 4/5: Generating AI summaries...")
    summaries = summarize_articles(recent, top_indices, ai_client, args.lang)

    final_articles = []
    for idx in top_indices:
        a = recent[idx]
        s = top_scores[idx]
        sm = summaries.get(idx, {"title_zh": a.title, "summary": a.description[:200], "reason": ""})
        final_articles.append(ScoredArticle(
            title=a.title,
            link=a.link,
            pub_date=a.pub_date,
            description=a.description,
            source_name=a.source_name,
            source_url=a.source_url,
            score=s["relevance"] + s["quality"] + s["timeliness"],
            score_breakdown=ScoreBreakdown(
                relevance=s["relevance"],
                quality=s["quality"],
                timeliness=s["timeliness"],
            ),
            category=s["category"],
            keywords=s["keywords"],
            title_zh=sm.get("title_zh", ""),
            summary=sm.get("summary", ""),
            reason=sm.get("reason", ""),
        ))

    # Step 5: Highlights
    print("[digest] Step 5/5: Generating today's highlights...")
    highlights = generate_highlights(final_articles, ai_client, args.lang)

    # Generate report
    successful_sources = {a.source_name for a in all_articles}
    report = generate_report(
        articles=final_articles,
        highlights=highlights,
        total_feeds=len(RSS_FEEDS),
        success_feeds=len(successful_sources),
        total_articles=len(all_articles),
        filtered_articles=len(recent),
        hours=args.hours,
    )

    # Write output
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")

    print()
    print("[digest] ✅ Done!")
    print(f"[digest] 📁 Report: {output_path}")
    print(
        f"[digest] 📊 Stats: {len(successful_sources)} sources → "
        f"{len(all_articles)} articles → {len(recent)} recent → "
        f"{len(final_articles)} selected"
    )

    if final_articles:
        print()
        print("[digest] 🏆 Top 3 Preview:")
        for i in range(min(3, len(final_articles))):
            a = final_articles[i]
            print(f"  {i + 1}. {a.title_zh or a.title}")
            print(f"     {a.summary[:80]}...")


if __name__ == "__main__":
    main()
