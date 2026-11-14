from __future__ import annotations

import re

PLATFORM_LIMITS = {"instagram": 2200, "tiktok": 2200, "x": 280}


def _keywords(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9]{3,}", text.lower())
    blocked = {"this", "that", "with", "from", "your", "have", "about", "video", "into", "will"}
    seen: list[str] = []
    for word in words:
        if word not in blocked and word not in seen:
            seen.append(word)
    return seen[:5]


def adapt_content(title: str, notes: str, platform: str) -> dict[str, str]:
    clean = " ".join(notes.split())
    tags = _keywords(f"{title} {clean}")
    hashtags = " ".join(f"#{word.title()}" for word in tags)

    if platform == "instagram":
        caption = f"{title}\n\n{clean}\n\nSave this post and share your take below."
    elif platform == "tiktok":
        caption = f"{title}: {clean} What would you try first?"
    elif platform == "x":
        caption = f"{title}: {clean}"
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    limit = PLATFORM_LIMITS[platform]
    reserved = len(hashtags) + 1 if hashtags else 0
    caption = caption[: max(1, limit - reserved)].rstrip()
    return {"caption": caption, "hashtags": hashtags}

