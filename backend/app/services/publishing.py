from __future__ import annotations

from datetime import UTC, datetime

from ..db import db, now_iso
from .connectors import connector_for


def publish_post(post_id: int) -> dict:
    with db() as connection:
        post = connection.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not post:
            raise LookupError("Post not found")
        if post["status"] == "published":
            return dict(post)
        try:
            result = connector_for(post["platform"]).publish(post_id, post["caption"])
            connection.execute(
                """UPDATE posts SET status='published', published_at=?, external_id=?,
                error_message=NULL, updated_at=? WHERE id=?""",
                (result.published_at, result.external_id, now_iso(), post_id),
            )
        except Exception as exc:
            connection.execute(
                "UPDATE posts SET status='failed', error_message=?, updated_at=? WHERE id=?",
                (str(exc), now_iso(), post_id),
            )
            raise
        return dict(connection.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone())


def process_due_posts() -> int:
    now = datetime.now(UTC).isoformat()
    with db() as connection:
        due = connection.execute(
            "SELECT id FROM posts WHERE status='scheduled' AND scheduled_at <= ? ORDER BY scheduled_at",
            (now,),
        ).fetchall()
    for row in due:
        publish_post(row["id"])
    return len(due)

