# -*- coding: utf-8 -*-
"""数据模型定义。"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import List


@dataclass
class Article:
    """从 RSS 抓取的原始文章。"""

    title: str
    link: str
    pub_date: datetime
    description: str
    source_name: str
    source_url: str


@dataclass
class ScoreBreakdown:
    """AI 三维评分。"""

    relevance: int = 5
    quality: int = 5
    timeliness: int = 5


@dataclass
class ScoredArticle:
    """经过 AI 评分、分类、摘要的最终文章。"""

    title: str
    link: str
    pub_date: datetime
    description: str
    source_name: str
    source_url: str
    score: int
    score_breakdown: ScoreBreakdown
    category: str
    keywords: List[str] = field(default_factory=list)
    title_zh: str = ""
    summary: str = ""
    reason: str = ""
