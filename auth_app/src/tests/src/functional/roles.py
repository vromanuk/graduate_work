from http import HTTPStatus

ROLES_ENDPOINT = "/api/v1/roles"


def test_get_all_roles(client, access_token_admin):
    resp = client.get(ROLES_ENDPOINT, headers=access_token_admin)
    assert resp.status_code == HTTPStatus.OK


def test_get_all_roles_forbidden(client, access_token_admin):
    resp = client.get(ROLES_ENDPOINT, headers=access_token_admin)
    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_get_all_roles_without_jwt(client):
    resp = client.get(ROLES_ENDPOINT)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
