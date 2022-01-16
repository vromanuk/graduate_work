import uuid
from http import HTTPStatus

import pytest
from flask_jwt_extended import create_access_token

from src import create_app
from src.database.db import session_scope
from src.database.models import User
from src.tests.src.functional.auth import register


@pytest.fixture
def client():
    app = create_app()

    with app.test_client() as client:
        yield client


@pytest.fixture
def registered_user(client):
    login = str(uuid.uuid4())
    password = str(uuid.uuid4())

    resp = register(client, login, password)
    assert resp.status_code == HTTPStatus.CREATED

    return login, password


@pytest.fixture
def access_token_admin(registered_user):
    user_login, password = registered_user
    additional_claims = {"perm": 255}
    access_token = create_access_token(user_login, additional_claims=additional_claims)
    headers = {"Authorization": "Bearer {}".format(access_token)}

    return headers


@pytest.fixture
def user(client) -> User:
    login = str(uuid.uuid4())
    password = str(uuid.uuid4())

    resp = register(client, login, password)
    assert resp.status_code == HTTPStatus.CREATED

    with session_scope() as session:
        return session.query(User).filter_by(login=login).first()
