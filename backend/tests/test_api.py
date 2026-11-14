from __future__ import annotations


def test_end_to_end_content_workflow(client, auth_headers):
    created = client.post(
        "/api/content",
        headers=auth_headers,
        json={
            "title": "Campus creator tips",
            "source_notes": "Three practical ways to plan a weekly content schedule.",
            "platforms": ["instagram", "tiktok", "x"],
        },
    )
    assert created.status_code == 201
    payload = created.json()
    assert len(payload["posts"]) == 3
    assert {post["platform"] for post in payload["posts"]} == {"instagram", "tiktok", "x"}

    post_id = payload["posts"][0]["id"]
    edited = client.patch(
        f"/api/posts/{post_id}",
        headers=auth_headers,
        json={"caption": "Edited by the creator", "hashtags": "#Campus"},
    )
    assert edited.status_code == 200
    assert edited.json()["caption"] == "Edited by the creator"

    published = client.post(f"/api/posts/{post_id}/publish", headers=auth_headers)
    assert published.status_code == 200
    assert published.json()["status"] == "published"
    assert published.json()["external_id"].startswith("demo_")

    dashboard = client.get("/api/dashboard", headers=auth_headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["status_counts"]["published"] == 1


def test_rejects_unauthenticated_requests(client):
    response = client.get("/api/content")
    assert response.status_code == 401

