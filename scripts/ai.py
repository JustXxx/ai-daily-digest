# -*- coding: utf-8 -*-
"""AI 调用客户端与评分、摘要、看点生成逻辑。"""

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict
from typing import List

import requests

from .constants import AI_BATCH_SIZE
from .constants import CATEGORY_META
from .constants import GEMINI_API_URL
from .constants import OPENAI_DEFAULT_API_BASE
from .constants import OPENAI_DEFAULT_MODEL
from .constants import VALID_CATEGORIES
from .models import Article
from .models import ScoredArticle

# ============================================================================
# Prompt Templates
# ============================================================================

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    """从 prompts/ 目录加载模板文件。"""
    path = _PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


# ============================================================================
# AI Providers (Gemini + OpenAI-compatible fallback)
# ============================================================================

def _call_gemini(prompt: str, api_key: str) -> str:
    """调用 Gemini API。"""
    resp = requests.post(
        f"{GEMINI_API_URL}?key={api_key}",
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "topP": 0.8,
                "topK": 40,
            },
        },
        timeout=120,
    )
    if not resp.ok:
        raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text[:500]}")

    data = resp.json()
    candidates = data.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "")
    return ""


def _call_openai_compatible(
    prompt: str,
    api_key: str,
    api_base: str,
    model: str,
) -> str:
    """调用 OpenAI 兼容接口。"""
    base = api_base.rstrip("/")
    resp = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "top_p": 0.8,
        },
        timeout=120,
    )
    if not resp.ok:
        raise RuntimeError(f"OpenAI-compatible API error ({resp.status_code}): {resp.text[:500]}")

    data = resp.json()
    choices = data.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                item.get("text", "")
                for item in content
                if item.get("type") == "text"
            )
    return ""


def _infer_openai_model(api_base: str) -> str:
    """根据 API base URL 推断模型名。"""
    if "deepseek" in api_base.lower():
        return "deepseek-chat"
    return OPENAI_DEFAULT_MODEL


class AIClient:
    """AI 调用客户端，Gemini 优先、OpenAI 兼容自动降级。"""

    def __init__(
        self,
        gemini_api_key: str = "",
        openai_api_key: str = "",
        openai_api_base: str = "",
        openai_model: str = "",
    ) -> None:
        self._gemini_key = gemini_api_key.strip()
        self._openai_key = openai_api_key.strip()
        self._openai_base = (openai_api_base.strip() or OPENAI_DEFAULT_API_BASE).rstrip("/")
        self._openai_model = openai_model.strip() or _infer_openai_model(self._openai_base)
        self._gemini_enabled = bool(self._gemini_key)
        self._fallback_logged = False

    @property
    def openai_base(self) -> str:
        return self._openai_base

    @property
    def openai_model(self) -> str:
        return self._openai_model

    def call(self, prompt: str) -> str:
        """调用 AI，Gemini 失败自动降级。"""
        if self._gemini_enabled and self._gemini_key:
            try:
                return _call_gemini(prompt, self._gemini_key)
            except Exception as exc:
                if self._openai_key:
                    if not self._fallback_logged:
                        print(
                            f"[digest] Gemini failed, switching to OpenAI-compatible "
                            f"fallback ({self._openai_base}, model={self._openai_model}). "
                            f"Reason: {exc}",
                            file=sys.stderr,
                        )
                        self._fallback_logged = True
                    self._gemini_enabled = False
                    return _call_openai_compatible(
                        prompt, self._openai_key, self._openai_base, self._openai_model,
                    )
                raise

        if self._openai_key:
            return _call_openai_compatible(
                prompt, self._openai_key, self._openai_base, self._openai_model,
            )

        raise RuntimeError(
            "No AI API key configured. Set GEMINI_API_KEY and/or OPENAI_API_KEY."
        )


def _parse_json_response(text: str) -> dict:
    """解析 AI 返回的 JSON（兼容 markdown 代码块包裹）。"""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return json.loads(cleaned)


# ============================================================================
# AI Scoring
# ============================================================================

def _build_scoring_prompt(articles: List[Dict[str, str]]) -> str:
    """构建评分 prompt。"""
    parts = []
    for a in articles:
        parts.append(
            f"Index {a['index']}: [{a['source_name']}] {a['title']}\n"
            f"{a['description'][:300]}"
        )
    articles_text = "\n\n---\n\n".join(parts)

    template = _load_prompt("scoring.txt")
    return template.format_map({
        "article_count": len(articles),
        "articles_text": articles_text,
    })


def _clamp(v: int, lo: int = 1, hi: int = 10) -> int:
    return max(lo, min(hi, round(v)))


def score_articles(
    articles: List[Article],
    ai_client: AIClient,
) -> Dict[int, Dict]:
    """对所有文章进行 AI 评分，返回 {index: score_dict}。"""
    all_scores: Dict[int, Dict] = {}

    indexed = [
        {
            "index": i,
            "title": a.title,
            "description": a.description,
            "source_name": a.source_name,
        }
        for i, a in enumerate(articles)
    ]

    batches = [
        indexed[i:i + AI_BATCH_SIZE]
        for i in range(0, len(indexed), AI_BATCH_SIZE)
    ]

    print(f"[digest] AI scoring: {len(articles)} articles in {len(batches)} batches")

    for batch_idx, batch in enumerate(batches):
        try:
            prompt = _build_scoring_prompt(batch)
            response_text = ai_client.call(prompt)
            parsed = _parse_json_response(response_text)

            for result in parsed.get("results", []):
                cat = result.get("category", "other")
                if cat not in VALID_CATEGORIES:
                    cat = "other"
                kw = result.get("keywords", [])
                if not isinstance(kw, list):
                    kw = []
                all_scores[result["index"]] = {
                    "relevance": _clamp(result.get("relevance", 5)),
                    "quality": _clamp(result.get("quality", 5)),
                    "timeliness": _clamp(result.get("timeliness", 5)),
                    "category": cat,
                    "keywords": kw[:4],
                }
        except Exception as exc:
            print(f"[digest] Scoring batch {batch_idx} failed: {exc}", file=sys.stderr)
            for item in batch:
                all_scores[item["index"]] = {
                    "relevance": 5,
                    "quality": 5,
                    "timeliness": 5,
                    "category": "other",
                    "keywords": [],
                }

        print(f"[digest] Scoring progress: {batch_idx + 1}/{len(batches)} batches")

    return all_scores


# ============================================================================
# AI Summarization
# ============================================================================

def _build_summary_prompt(articles: List[Dict[str, str]], lang: str) -> str:
    """构建摘要 prompt。"""
    parts = []
    for a in articles:
        parts.append(
            f"Index {a['index']}: [{a['source_name']}] {a['title']}\n"
            f"URL: {a['link']}\n{a['description'][:800]}"
        )
    articles_text = "\n\n---\n\n".join(parts)

    template_name = "summary_zh.txt" if lang == "zh" else "summary_en.txt"
    template = _load_prompt(template_name)
    return template.format_map({
        "article_count": len(articles),
        "articles_text": articles_text,
    })


def summarize_articles(
    articles: List[Article],
    indices: List[int],
    ai_client: AIClient,
    lang: str,
) -> Dict[int, Dict[str, str]]:
    """为 top 文章生成摘要。"""
    summaries: Dict[int, Dict[str, str]] = {}

    indexed = [
        {
            "index": i,
            "title": articles[i].title,
            "description": articles[i].description,
            "source_name": articles[i].source_name,
            "link": articles[i].link,
        }
        for i in indices
    ]

    batches = [
        indexed[i:i + AI_BATCH_SIZE]
        for i in range(0, len(indexed), AI_BATCH_SIZE)
    ]

    print(f"[digest] Generating summaries for {len(indices)} articles in {len(batches)} batches")

    for batch_idx, batch in enumerate(batches):
        try:
            prompt = _build_summary_prompt(batch, lang)
            response_text = ai_client.call(prompt)
            parsed = _parse_json_response(response_text)

            for result in parsed.get("results", []):
                summaries[result["index"]] = {
                    "title_zh": result.get("titleZh", ""),
                    "summary": result.get("summary", ""),
                    "reason": result.get("reason", ""),
                }
        except Exception as exc:
            print(f"[digest] Summary batch {batch_idx} failed: {exc}", file=sys.stderr)
            for item in batch:
                idx = item["index"]
                summaries[idx] = {
                    "title_zh": item["title"],
                    "summary": item["title"],
                    "reason": "",
                }

        print(f"[digest] Summary progress: {batch_idx + 1}/{len(batches)} batches")

    return summaries


# ============================================================================
# AI Highlights (Today's Trends)
# ============================================================================

def generate_highlights(
    articles: List[ScoredArticle],
    ai_client: AIClient,
    lang: str,
) -> str:
    """生成今日看点总结。"""
    article_list = "\n".join(
        f"{i + 1}. [{a.category}] {a.title_zh or a.title}\n   {a.summary[:200]}"
        for i, a in enumerate(articles[:10])
    )

    # 提取分类分布信息
    cat_counts = Counter(a.category for a in articles)
    cat_summary = ", ".join(
        f"{CATEGORY_META.get(c, {}).get('label', c)} {n}篇"
        for c, n in cat_counts.most_common()
    )

    template_name = "highlights_zh.txt" if lang == "zh" else "highlights_en.txt"
    template = _load_prompt(template_name)
    prompt = template.format_map({
        "cat_summary": cat_summary,
        "article_list": article_list,
    })

    try:
        return ai_client.call(prompt).strip()
    except Exception as exc:
        print(f"[digest] Highlights generation failed: {exc}", file=sys.stderr)
        return ""
