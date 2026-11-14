from __future__ import annotations

import json
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import ALLOWED_ORIGINS, MAX_UPLOAD_BYTES, UPLOAD_DIR
from .db import db, init_db, now_iso
from .schemas import ContentCreate, LoginRequest, PostUpdate, RegisterRequest, ScheduleRequest
from .security import hash_password, new_token, verify_password
from .services.adaptation import adapt_content
from .services.publishing import process_due_posts, publish_post


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="OmniPost API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authentication token")
    token = authorization.removeprefix("Bearer ").strip()
    with db() as connection:
        row = connection.execute(
            """SELECT users.id, users.email, users.name FROM sessions
            JOIN users ON users.id = sessions.user_id WHERE sessions.token = ?""",
            (token,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return dict(row)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> dict:
    email = payload.email.strip().lower()
    try:
        with db() as connection:
            cursor = connection.execute(
                "INSERT INTO users(email, name, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (email, payload.name.strip(), hash_password(payload.password), now_iso()),
            )
            user_id = cursor.lastrowid
            token = new_token()
            connection.execute(
                "INSERT INTO sessions(token, user_id, created_at) VALUES (?, ?, ?)",
                (token, user_id, now_iso()),
            )
    except Exception as exc:
        if "UNIQUE" in str(exc):
            raise HTTPException(status_code=409, detail="An account already exists for this email") from exc
        raise
    return {"token": token, "user": {"id": user_id, "email": email, "name": payload.name.strip()}}


@app.post("/api/auth/login")
def login(payload: LoginRequest) -> dict:
    with db() as connection:
        row = connection.execute("SELECT * FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
        if not row or not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        token = new_token()
        connection.execute(
            "INSERT INTO sessions(token, user_id, created_at) VALUES (?, ?, ?)",
            (token, row["id"], now_iso()),
        )
    return {"token": token, "user": {"id": row["id"], "email": row["email"], "name": row["name"]}}


@app.get("/api/me")
def me(user: dict = Depends(require_user)) -> dict:
    return user


@app.post("/api/media", status_code=status.HTTP_201_CREATED)
async def upload_media(file: UploadFile = File(...), user: dict = Depends(require_user)) -> dict:
    allowed = {"video/mp4", "video/quicktime", "video/webm", "image/jpeg", "image/png"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Upload MP4, MOV, WebM, JPEG, or PNG media")
    suffix = Path(file.filename or "upload.bin").suffix.lower()
    stored_name = f"{uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / stored_name
    size = 0
    with destination.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                output.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Upload exceeds the configured size limit")
            output.write(chunk)
    with db() as connection:
        cursor = connection.execute(
            """INSERT INTO media(user_id, original_name, stored_name, content_type, size_bytes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user["id"], file.filename or stored_name, stored_name, file.content_type, size, now_iso()),
        )
        media_id = cursor.lastrowid
    return {"id": media_id, "original_name": file.filename, "content_type": file.content_type, "size_bytes": size}


@app.get("/api/media/{media_id}/download")
def download_media(media_id: int, user: dict = Depends(require_user)):
    with db() as connection:
        row = connection.execute(
            "SELECT * FROM media WHERE id = ? AND user_id = ?", (media_id, user["id"])
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Media not found")
    return FileResponse(UPLOAD_DIR / row["stored_name"], media_type=row["content_type"], filename=row["original_name"])


@app.post("/api/content", status_code=status.HTTP_201_CREATED)
def create_content(payload: ContentCreate, user: dict = Depends(require_user)) -> dict:
    with db() as connection:
        if payload.media_id:
            owns_media = connection.execute(
                "SELECT id FROM media WHERE id=? AND user_id=?", (payload.media_id, user["id"])
            ).fetchone()
            if not owns_media:
                raise HTTPException(status_code=404, detail="Media not found")
        cursor = connection.execute(
            "INSERT INTO content_items(user_id, media_id, title, source_notes, created_at) VALUES (?, ?, ?, ?, ?)",
            (user["id"], payload.media_id, payload.title.strip(), payload.source_notes.strip(), now_iso()),
        )
        content_id = cursor.lastrowid
        post_ids = []
        for platform in dict.fromkeys(payload.platforms):
            adaptation = adapt_content(payload.title, payload.source_notes, platform)
            post_cursor = connection.execute(
                """INSERT INTO posts(content_id, platform, caption, hashtags, status, updated_at)
                VALUES (?, ?, ?, ?, 'draft', ?)""",
                (content_id, platform, adaptation["caption"], adaptation["hashtags"], now_iso()),
            )
            post_ids.append(post_cursor.lastrowid)
    return get_content(content_id, user)


@app.get("/api/content")
def list_content(user: dict = Depends(require_user)) -> list[dict]:
    with db() as connection:
        items = connection.execute(
            "SELECT * FROM content_items WHERE user_id = ? ORDER BY created_at DESC", (user["id"],)
        ).fetchall()
        result = []
        for item in items:
            posts = connection.execute("SELECT * FROM posts WHERE content_id = ? ORDER BY id", (item["id"],)).fetchall()
            record = dict(item)
            record["posts"] = [dict(post) for post in posts]
            result.append(record)
    return result


@app.get("/api/content/{content_id}")
def get_content(content_id: int, user: dict = Depends(require_user)) -> dict:
    with db() as connection:
        item = connection.execute(
            "SELECT * FROM content_items WHERE id=? AND user_id=?", (content_id, user["id"])
        ).fetchone()
        if not item:
            raise HTTPException(status_code=404, detail="Content not found")
        posts = connection.execute("SELECT * FROM posts WHERE content_id=? ORDER BY id", (content_id,)).fetchall()
    result = dict(item)
    result["posts"] = [dict(post) for post in posts]
    return result


def owned_post(post_id: int, user_id: int):
    with db() as connection:
        row = connection.execute(
            """SELECT posts.* FROM posts JOIN content_items ON content_items.id=posts.content_id
            WHERE posts.id=? AND content_items.user_id=?""",
            (post_id, user_id),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return row


@app.patch("/api/posts/{post_id}")
def update_post(post_id: int, payload: PostUpdate, user: dict = Depends(require_user)) -> dict:
    owned_post(post_id, user["id"])
    with db() as connection:
        connection.execute(
            "UPDATE posts SET caption=?, hashtags=?, updated_at=? WHERE id=?",
            (payload.caption, payload.hashtags, now_iso(), post_id),
        )
        row = connection.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    return dict(row)


@app.post("/api/posts/{post_id}/schedule")
def schedule_post(post_id: int, payload: ScheduleRequest, user: dict = Depends(require_user)) -> dict:
    owned_post(post_id, user["id"])
    scheduled = payload.scheduled_at.isoformat()
    with db() as connection:
        connection.execute(
            """UPDATE posts SET status='scheduled', scheduled_at=?, published_at=NULL,
            external_id=NULL, error_message=NULL, updated_at=? WHERE id=?""",
            (scheduled, now_iso(), post_id),
        )
        row = connection.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    return dict(row)


@app.post("/api/posts/{post_id}/publish")
def publish(post_id: int, user: dict = Depends(require_user)) -> dict:
    owned_post(post_id, user["id"])
    try:
        return publish_post(post_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/jobs/run-due")
def run_due(user: dict = Depends(require_user)) -> dict:
    return {"processed": process_due_posts()}


@app.get("/api/dashboard")
def dashboard(user: dict = Depends(require_user)) -> dict:
    with db() as connection:
        counts = connection.execute(
            """SELECT posts.status, COUNT(*) AS total FROM posts
            JOIN content_items ON content_items.id=posts.content_id
            WHERE content_items.user_id=? GROUP BY posts.status""",
            (user["id"],),
        ).fetchall()
        platform_rows = connection.execute(
            """SELECT posts.platform, COUNT(*) AS posts, COALESCE(SUM(views),0) AS views,
            COALESCE(SUM(engagements),0) AS engagements FROM posts
            JOIN content_items ON content_items.id=posts.content_id
            WHERE content_items.user_id=? GROUP BY posts.platform""",
            (user["id"],),
        ).fetchall()
        upcoming = connection.execute(
            """SELECT posts.*, content_items.title FROM posts
            JOIN content_items ON content_items.id=posts.content_id
            WHERE content_items.user_id=? AND posts.status='scheduled'
            ORDER BY posts.scheduled_at LIMIT 6""",
            (user["id"],),
        ).fetchall()
    return {
        "status_counts": {row["status"]: row["total"] for row in counts},
        "platforms": [dict(row) for row in platform_rows],
        "upcoming": [dict(row) for row in upcoming],
    }

