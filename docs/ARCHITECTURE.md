# OmniPost architecture

## System map

```text
Browser (Next.js)
       |
       | JSON and multipart HTTP
       v
FastAPI application ---- SQLite database
       |                       |
       |                       +-- users, sessions, content, posts
       |
       +-- local object storage (uploaded media)
       |
       +-- adaptation service
       |
       +-- connector interface ---- Instagram demo connector
                              |---- TikTok demo connector
                              +---- X demo connector

Scheduler worker polls due posts and calls the same connector interface.
```

## Design decisions

- **SQLite for the reproducible demo.** The proposal specified PostgreSQL, but a file database removes installation friction and supports the complete MVP. The SQL is deliberately portable so PostgreSQL can replace it later.
- **Opaque server-side sessions.** Passwords use PBKDF2-HMAC-SHA256 with a random salt. Session tokens are random and stored server-side. The repository contains no secrets.
- **Local media storage.** The storage boundary lives behind the media API. S3 or Cloudflare R2 can replace the local volume without changing the frontend workflow.
- **Deterministic adaptation.** The included service creates platform-specific captions without requiring a paid AI key. A production adapter can call a speech-to-text and language model provider.
- **Demo connectors.** Each connector implements a common `publish` method and returns an idempotent-looking external ID. This demonstrates orchestration safely while platform app review remains out of project scope.
- **Separate scheduler.** The worker polls scheduled rows every 15 seconds. It can scale independently and keeps delayed work outside HTTP requests.

## Post state model

```text
draft -> scheduled -> published
  |                       ^
  +-----------------------+

Any connector exception moves a post to failed. Editing is allowed before or after scheduling.
```

## Production hardening roadmap

1. Replace SQLite with PostgreSQL and add schema migrations.
2. Move uploads to S3 or R2 using signed upload URLs.
3. Encrypt OAuth refresh tokens through a managed key service.
4. Add Celery or a managed queue with retry backoff and idempotency keys.
5. Complete Meta, TikTok, and X app review, then add real connectors behind feature flags.
6. Ingest platform metrics through scheduled synchronization jobs.

