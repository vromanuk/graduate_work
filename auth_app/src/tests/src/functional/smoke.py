from http import HTTPStatus


def test_smoke(client):
    resp = client.get("/api/v1/smoke")
    assert resp.status_code == HTTPStatus.OK


def test_smoke_too_many_requests(client):
    for _ in range(4):
        resp = client.get("/api/v1/smoke")
    assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS
