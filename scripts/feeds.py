# -*- coding: utf-8 -*-
"""RSS / Atom 解析与并发抓取。"""

import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from datetime import datetime
from datetime import timezone
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import requests

from .constants import FEED_CONCURRENCY
from .constants import FEED_FETCH_TIMEOUT_S
from .models import Article

# ============================================================================
# XML Parsing Helpers
# ============================================================================

_ATOM_NS = "http://www.w3.org/2005/Atom"
_DC_NS = "http://purl.org/dc/elements/1.1/"
_CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"

_HTML_TAG_RE = re.compile(r"<[^>]*>")
_HTML_ENTITIES = {
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
    "&nbsp;": " ",
}


def _strip_html(html: str) -> str:
    """移除 HTML 标签和常见实体。"""
    text = _HTML_TAG_RE.sub("", html)
    for entity, char in _HTML_ENTITIES.items():
        text = text.replace(entity, char)
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    return text.strip()


def _parse_date(date_str: str) -> Optional[datetime]:
    """尝试多种格式解析日期字符串。"""
    if not date_str:
        return None

    date_str = date_str.strip()

    # ISO 8601 / RFC 3339
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    # RFC 822 (RSS 2.0)
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%d %b %Y %H:%M:%S %z",
    ):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    # 兜底: 去掉时区缩写后再试
    cleaned = re.sub(r"\s+[A-Z]{2,4}$", "", date_str)
    for fmt in ("%a, %d %b %Y %H:%M:%S", "%d %b %Y %H:%M:%S"):
        try:
            return datetime.strptime(cleaned, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def _get_text(element: Optional[ET.Element]) -> str:
    """安全获取 XML element 文本。"""
    if element is None:
        return ""
    return (element.text or "").strip()


def _parse_feed_xml(xml_text: str) -> List[Dict[str, str]]:
    """解析 RSS 2.0 或 Atom 格式的 XML，返回文章列表。"""
    items: List[Dict[str, str]] = []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

    # Atom feed
    if root.tag == f"{{{_ATOM_NS}}}feed" or root.tag == "feed":
        ns = {"atom": _ATOM_NS}
        entries = root.findall("atom:entry", ns)
        if not entries:
            entries = root.findall("entry")

        for entry in entries:
            title = _get_text(entry.find("atom:title", ns)) or _get_text(entry.find("title"))

            link = ""
            for link_el in entry.findall("atom:link", ns) + entry.findall("link"):
                rel = link_el.get("rel", "alternate")
                if rel == "alternate":
                    link = link_el.get("href", "")
                    break
            if not link:
                link_el = entry.find("atom:link", ns) or entry.find("link")
                if link_el is not None:
                    link = link_el.get("href", "")

            pub_date = (
                _get_text(entry.find("atom:published", ns))
                or _get_text(entry.find("published"))
                or _get_text(entry.find("atom:updated", ns))
                or _get_text(entry.find("updated"))
            )

            desc_raw = (
                _get_text(entry.find("atom:summary", ns))
                or _get_text(entry.find("summary"))
                or _get_text(entry.find("atom:content", ns))
                or _get_text(entry.find("content"))
            )
            description = _strip_html(desc_raw)[:500]

            if title or link:
                items.append({
                    "title": _strip_html(title),
                    "link": link,
                    "pub_date": pub_date,
                    "description": description,
                })

    else:
        # RSS 2.0: <rss><channel><item>
        channel = root.find("channel")
        if channel is None:
            channel = root

        for item in channel.findall("item"):
            title = _strip_html(_get_text(item.find("title")))
            link = _get_text(item.find("link")) or _get_text(item.find("guid"))
            pub_date = (
                _get_text(item.find("pubDate"))
                or _get_text(item.find(f"{{{_DC_NS}}}date"))
                or _get_text(item.find("date"))
            )
            desc_raw = (
                _get_text(item.find("description"))
                or _get_text(item.find(f"{{{_CONTENT_NS}}}encoded"))
            )
            description = _strip_html(desc_raw)[:500]

            if title or link:
                items.append({
                    "title": title,
                    "link": link,
                    "pub_date": pub_date,
                    "description": description,
                })

    return items


# ============================================================================
# Feed Fetching
# ============================================================================

_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": "AI-Daily-Digest/1.0 (RSS Reader; Python)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
})


def _fetch_feed(feed: Dict[str, str]) -> List[Article]:
    """抓取单个 RSS 源，返回文章列表。失败返回空列表。"""
    try:
        resp = _SESSION.get(feed["xml_url"], timeout=FEED_FETCH_TIMEOUT_S)
        resp.raise_for_status()
        items = _parse_feed_xml(resp.text)
        return [
            Article(
                title=item["title"],
                link=item["link"],
                pub_date=_parse_date(item["pub_date"]) or datetime(1970, 1, 1, tzinfo=timezone.utc),
                description=item["description"],
                source_name=feed["name"],
                source_url=feed["html_url"],
            )
            for item in items
        ]
    except requests.exceptions.Timeout:
        print(f"[digest] ✗ {feed['name']}: timeout", file=sys.stderr)
        return []
    except Exception as exc:
        print(f"[digest] ✗ {feed['name']}: {exc}", file=sys.stderr)
        return []


def fetch_all_feeds(feeds: List[Dict[str, str]]) -> Tuple[List[Article], int, int]:
    """并发抓取所有 RSS 源。返回 (文章列表, 成功源数, 失败源数)。"""
    all_articles: List[Article] = []
    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=FEED_CONCURRENCY) as pool:
        future_to_feed = {pool.submit(_fetch_feed, f): f for f in feeds}
        done_count = 0
        for future in as_completed(future_to_feed):
            done_count += 1
            articles = future.result()
            if articles:
                all_articles.extend(articles)
                success_count += 1
            else:
                fail_count += 1

            if done_count % FEED_CONCURRENCY == 0 or done_count == len(feeds):
                print(
                    f"[digest] Progress: {done_count}/{len(feeds)} feeds "
                    f"processed ({success_count} ok, {fail_count} failed)"
                )

    print(
        f"[digest] Fetched {len(all_articles)} articles "
        f"from {success_count} feeds ({fail_count} failed)"
    )
    return all_articles, success_count, fail_count
