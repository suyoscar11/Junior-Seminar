# API reference

Interactive OpenAPI documentation is available at `http://localhost:8000/docs` while the API runs.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/auth/register` | Create a user and session |
| `POST` | `/api/auth/login` | Create a session |
| `GET` | `/api/me` | Return the authenticated user |
| `POST` | `/api/media` | Upload supported media |
| `GET` | `/api/media/{id}/download` | Download owned media |
| `POST` | `/api/content` | Create a content item and platform adaptations |
| `GET` | `/api/content` | List owned content and posts |
| `PATCH` | `/api/posts/{id}` | Edit a caption and hashtags |
| `POST` | `/api/posts/{id}/schedule` | Schedule a post |
| `POST` | `/api/posts/{id}/publish` | Publish through a demo connector |
| `POST` | `/api/jobs/run-due` | Manually process due jobs |
| `GET` | `/api/dashboard` | Return status and platform summaries |

All routes except registration, login, and health require `Authorization: Bearer <token>`.

