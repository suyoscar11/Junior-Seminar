from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    upload_path = tmp_path / "uploads"
    monkeypatch.setenv("OMNIPOST_DATABASE_PATH", str(db_path))
    monkeypatch.setenv("OMNIPOST_UPLOAD_DIR", str(upload_path))

    import app.config as config
    import app.db as database

    config.DATABASE_PATH = db_path
    config.UPLOAD_DIR = upload_path
    database.DATABASE_PATH = db_path
    upload_path.mkdir()

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={"name": "Test Creator", "email": "creator@example.com", "password": "testpass123"},
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['token']}"}

