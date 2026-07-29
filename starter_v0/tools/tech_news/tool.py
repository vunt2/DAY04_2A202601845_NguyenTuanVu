from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import requests

from tools._shared import TIMEOUT, err


HN_API = "https://hacker-news.firebaseio.com/v0"
STORY_ENDPOINTS = {"top": "topstories", "new": "newstories"}


def _story_item(raw: dict[str, Any]) -> dict[str, Any]:
    story_id = raw.get("id")
    external_url = raw.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
    timestamp = raw.get("time")
    published_at = (
        datetime.fromtimestamp(timestamp, tz=UTC).isoformat().replace("+00:00", "Z")
        if isinstance(timestamp, (int, float))
        else None
    )
    return {
        "title": raw.get("title") or "Untitled Hacker News story",
        "url": external_url,
        "source": "Hacker News",
        "summary": (raw.get("text") or "").strip(),
        "published_at": published_at,
        "story_id": story_id,
        "discussion_url": f"https://news.ycombinator.com/item?id={story_id}",
        "score": raw.get("score"),
        "comments": raw.get("descendants", 0),
        "by": raw.get("by"),
    }


def get_tech_news(mode: str = "top", limit: int = 5, query: str = "") -> dict[str, Any]:
    """Return top or newest Hacker News stories, optionally filtered by keywords."""
    try:
        selected_mode = (mode or "top").strip().lower()
        if selected_mode not in STORY_ENDPOINTS:
            raise ValueError("mode must be 'top' or 'new'")
        selected_limit = max(1, min(int(limit or 5), 10))
        keywords = [word.lower() for word in (query or "").split() if word.strip()]

        response = requests.get(f"{HN_API}/{STORY_ENDPOINTS[selected_mode]}.json", timeout=TIMEOUT)
        response.raise_for_status()
        story_ids = response.json() or []

        items: list[dict[str, Any]] = []
        # Fetch a bounded window so keyword filtering has useful candidates.
        scan_limit = 50 if keywords else selected_limit
        for story_id in story_ids[:scan_limit]:
            story_response = requests.get(f"{HN_API}/item/{story_id}.json", timeout=TIMEOUT)
            story_response.raise_for_status()
            story = story_response.json() or {}
            if story.get("type") != "story" or story.get("dead") or story.get("deleted"):
                continue
            searchable = f"{story.get('title', '')} {story.get('text', '')}".lower()
            if keywords and not all(word in searchable for word in keywords):
                continue
            items.append(_story_item(story))
            if len(items) >= selected_limit:
                break

        return {
            "tool": "get_tech_news",
            "mode": selected_mode,
            "query": query,
            "items": items,
            "source_url": f"{HN_API}/{STORY_ENDPOINTS[selected_mode]}.json",
            "note": "Public Hacker News API; no API key is required.",
        }
    except Exception as exc:
        return err("get_tech_news", exc)
