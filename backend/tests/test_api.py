from fastapi.testclient import TestClient


def test_healthz(client: TestClient) -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_list_links(client: TestClient) -> None:
    r = client.post("/api/links", json={"url": "https://example.com/a"})
    assert r.status_code == 201
    body = r.json()
    assert body["original_url"] == "https://example.com/a"
    assert len(body["code"]) >= 4
    assert body["clicks"] == 0

    r2 = client.get("/api/links")
    assert r2.status_code == 200
    assert len(r2.json()) == 1


def test_redirect_records_click(client: TestClient) -> None:
    created = client.post("/api/links", json={"url": "https://example.com/x"}).json()
    code = created["code"]

    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "https://example.com/x"

    listing = client.get("/api/links").json()
    assert listing[0]["clicks"] == 1


def test_unknown_code_404(client: TestClient) -> None:
    r = client.get("/nonexistent", follow_redirects=False)
    assert r.status_code == 404


def test_delete_link(client: TestClient) -> None:
    created = client.post("/api/links", json={"url": "https://example.com/y"}).json()
    link_id = created["id"]
    r = client.delete(f"/api/links/{link_id}")
    assert r.status_code == 204
    assert client.get("/api/links").json() == []


def test_stats_for_link_with_clicks(client: TestClient) -> None:
    created = client.post("/api/links", json={"url": "https://example.com/s"}).json()
    code, link_id = created["code"], created["id"]
    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False)

    r = client.get(f"/api/links/{link_id}/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["total_clicks"] == 3
    assert len(body["daily"]) == 7
    assert sum(d["count"] for d in body["daily"]) == 3


def test_invalid_url_rejected(client: TestClient) -> None:
    r = client.post("/api/links", json={"url": "not-a-url"})
    assert r.status_code == 422
