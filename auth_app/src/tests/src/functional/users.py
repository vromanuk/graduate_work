from http import HTTPStatus

from src.database.db import session_scope
from src.database.models import Role, User
from src.proto import UserInfoRequest, UserInfoResponse

USERS_ENDPOINT = "/api/v1/users"


def test_update_user_info_without_jwt(client):
    resp = client.put(USERS_ENDPOINT)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_assign_role(client, user, access_token_admin):
    with session_scope() as session:
        assert user.role.name == "User"
        admin_role_id = (
            session.query(Role)
            .filter_by(permissions=0xFF)
            .with_entities(Role.id)
            .scalar()
        )

    resp = client.put(
        f"{USERS_ENDPOINT}/{user.id}/role/{admin_role_id}", headers=access_token_admin
    )
    assert resp.status_code == HTTPStatus.OK

    with session_scope() as session:
        updated_user = session.query(User).filter_by(login=user.login).first()
        assert updated_user.role.name == "Admin"


def test_reset_role(client, user, access_token_admin):
    assert user.role.name == "User"

    resp = client.delete(
        f"{USERS_ENDPOINT}/{user.id}/role/", headers=access_token_admin
    )
    assert resp.status_code == HTTPStatus.NO_CONTENT

    with session_scope() as session:
        user_with_reset_role = session.query(User).filter_by(login=user.login).first()
        assert not user_with_reset_role.role


def test_get_user_info(client, user, access_token_admin):
    payload = {"user_id": str(user.id)}
    message = UserInfoRequest.message(payload)
    resp = client.post(
        f"{USERS_ENDPOINT}",
        headers=access_token_admin,
        data=message.SerializeToString(),
    )
    assert resp.status_code == HTTPStatus.OK

    user_info = UserInfoResponse.decode(resp.data)
    assert user_info.user.id == str(user.id)
    assert user_info.user.login == (user.login or "")
    assert user_info.user.email == (user.email or "")
    assert user_info.user.role == user.role.name


def test_get_user_info_empty_payload(client, access_token_admin):
    resp = client.post(
        f"{USERS_ENDPOINT}",
        headers=access_token_admin,
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
