from http import HTTPStatus

from src.database.db import session_scope
from src.database.models import LogHistory


def register(client, user_login, password):
    return client.post(
        "/api/v1/register",
        json=dict(login=user_login, password=password),
        follow_redirects=True,
    )


def login(client, user_login, password):
    return client.post(
        "/api/v1/login",
        json=dict(login=user_login, password=password),
        follow_redirects=True,
    )


def test_register(client):
    resp = register(client, "test_user", "test_pass")
    assert resp.status_code == HTTPStatus.CREATED


def test_login(client, registered_user):
    user_login, password = registered_user

    resp = login(client, user_login, password)
    assert resp.status_code == HTTPStatus.OK
    assert resp.json["access_token"]
    assert resp.json["refresh_token"]
    assert resp.json["user_id"]

    with session_scope() as session:
        q = session.query(LogHistory).filter_by(user_id=resp.json["user_id"])
        log_history = session.query(q.exists()).scalar()

    assert log_history


def test_login_invalid_cred(client):
    resp = login(client, None, None)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert resp.json["message"] == "Invalid Credentials."
