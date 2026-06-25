"""Expandable crypto news cards for the dashboard."""

import html
import json
from typing import Any

import streamlit as st

SENTIMENT_STYLES = {
    "bullish": ("#2ee8a5", "Bullish"),
    "bearish": ("#ff6b7a", "Bearish"),
    "neutral": ("#7ec8ff", "Neutral"),
}


def _esc(text: str) -> str:
    return html.escape(text or "")


def _sentiment_icon(sentiment: str) -> str:
    s = (sentiment or "").lower()
    if s == "bullish":
        return "🟢"
    if s == "bearish":
        return "🔴"
    return "⚪"


def normalize_article(article: dict[str, Any]) -> dict[str, Any]:
    source = article.get("source", "")
    if isinstance(source, dict):
        source_name = source.get("name", "")
    else:
        source_name = str(source) if source else ""

    raw_date = article.get("pubDate") or article.get("publishedAt") or ""
    published = raw_date[:10] if raw_date else ""

    tags = article.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    return {
        "id": article.get("id", ""),
        "title": (article.get("title") or "").strip(),
        "description": (
            article.get("description")
            or article.get("summary")
            or article.get("content")
            or ""
        ).strip(),
        "url": article.get("link") or article.get("url") or "",
        "published": published,
        "time_ago": article.get("timeAgo", ""),
        "source": source_name or article.get("sourceKey", "Unknown"),
        "category": (article.get("category") or "general").replace("-", " ").title(),
        "sentiment": (article.get("sentiment") or "").lower(),
        "tags": tags[:6],
    }


def collect_articles(news_df, max_articles: int = 8) -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []
    seen: set[str] = set()

    for _, news_row in news_df.iterrows():
        try:
            raw = news_row["data"]
            if isinstance(raw, str):
                raw = json.loads(raw)
            for article in raw.get("articles", []):
                norm = normalize_article(article)
                key = norm["id"] or norm["title"]
                if not norm["title"] or key in seen:
                    continue
                seen.add(key)
                norm["ingested_at"] = news_row.get("ingested_at")
                articles.append(norm)
                if len(articles) >= max_articles:
                    return articles
        except Exception:
            continue

    return articles


def _expander_label(article: dict[str, Any]) -> str:
    icon = _sentiment_icon(article["sentiment"])
    title = article["title"]
    if len(title) > 72:
        title = title[:69] + "…"
    when = article["time_ago"] or article["published"] or "recent"
    return f"{icon} {title}  ·  {article['source']}  ·  {when}"


def _render_article_body(article: dict[str, Any]) -> None:
    sentiment = article["sentiment"]
    color, label = SENTIMENT_STYLES.get(sentiment, ("#7ec8ff", "Unrated"))

    meta_bits = [
        f"<span class='news-chip'>{_esc(article['source'])}</span>",
        f"<span class='news-chip'>{_esc(article['category'])}</span>",
    ]
    if article["published"]:
        meta_bits.append(f"<span class='news-chip'>{_esc(article['published'])}</span>")
    if article["time_ago"]:
        meta_bits.append(f"<span class='news-chip'>{_esc(article['time_ago'])}</span>")
    meta_bits.append(
        f"<span class='news-chip news-chip-sentiment' style='color:{color}; border-color:{color}44;'>"
        f"{label}</span>"
    )

    st.markdown(
        f"<div class='news-meta-row'>{''.join(meta_bits)}</div>",
        unsafe_allow_html=True,
    )

    if article["description"]:
        st.markdown("**TL;DR**")
        st.markdown(
            f"<div class='news-tldr'>{_esc(article['description'])}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("No summary available for this article — open the source link for full details.")

    if article["tags"]:
        tag_html = "".join(
            f"<span class='news-tag'>{_esc(tag)}</span>" for tag in article["tags"]
        )
        st.markdown(f"<div class='news-tags'>{tag_html}</div>", unsafe_allow_html=True)

    if article["url"]:
        st.link_button("Read full article →", article["url"], use_container_width=False)


def render_news_feed(news_df, max_articles: int = 8) -> int:
    articles = collect_articles(news_df, max_articles=max_articles)
    if not articles:
        return 0

    col_left, col_right = st.columns(2)
    for i, article in enumerate(articles):
        with col_left if i % 2 == 0 else col_right:
            with st.expander(_expander_label(article), expanded=False):
                _render_article_body(article)

    return len(articles)
