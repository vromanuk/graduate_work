from functools import wraps
from http import HTTPStatus
from typing import Union

from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, verify_jwt_in_request)
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from src.database.db import session_scope
from src.database.models import Role, User
from src.permissions import Permission


class AuthService:
    @classmethod
    def register(cls, user) -> bool:
        default_role_id = Role.fetch_default_role()
        with session_scope() as session:
            try:
                user.role_id = default_role_id
                session.add(user)
                session.commit()
                return True

            except IntegrityError:
                session.rollback()
                return False

    @classmethod
    def login(
        cls, login: str, password: str
    ) -> Union[tuple[bool, None], tuple[bool, dict]]:
        user = User.find_by_login(login)
        if not user or not check_password_hash(user.password, password):
            return False, None

        additional_claims = {"perm": user.role.permissions}
        access_token = create_access_token(
            identity=user.id, additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=user.id)
        token = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
        }
        return True, token


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            current_user_permissions = claims["perm"]
            if (current_user_permissions & permission) == permission:
                return f(*args, **kwargs)
            return {"message": "forbidden"}, HTTPStatus.FORBIDDEN

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
