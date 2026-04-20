def test_healthz_ok(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_docs_served(client):
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_exposes_all_routers(client):
    r = client.get("/openapi.json")
    paths = r.json()["paths"]
    for p in [
        "/auth/session",
        "/projects",
        "/uploads/presign",
        "/style/parse/text",
        "/renders",
        "/agent/register",
        "/renders/{render_id}/stream",
    ]:
        assert p in paths, f"missing {p}"
