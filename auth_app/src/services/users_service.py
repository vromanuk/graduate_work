import datetime
import string
from secrets import choice
from typing import Optional
from uuid import UUID

from flask import current_app
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from src import get_redis
from src.database.db import session_scope
from src.database.models import Role, User


class UserService:
    @classmethod
    def get_user_account_info(cls, current_user_id: UUID.hex) -> User:
        user = User.find_by_uuid(current_user_id)
        return user

    @classmethod
    def update(cls, current_user_id: UUID, updated_user: User) -> bool:
        user = User.find_by_uuid(current_user_id)
        if not user:
            return False

        with session_scope() as session:
            try:
                session.execute(
                    update(User)
                    .where(User.id == current_user_id)
                    .values(login=updated_user.login, password=updated_user.password)
                )
            except IntegrityError:
                session.rollback()
                current_app.logger.info("Cannot update these user")
                return False
        return True

    @classmethod
    def update_role(
        cls,
        user_id: UUID,
        role_id: Optional[int] = None,
        subscription: Optional[str] = None,
    ) -> bool:
        if not (role_id or subscription):
            raise ValueError("You must specify either `role_id` or `subscription`")

        user = User.find_by_uuid(user_id)
        if not user:
            return False

        if role_id:
            role = Role.fetch(role_id)
        else:
            role = Role.fetch_by_name(subscription)
        if not role:
            return False

        with session_scope() as session:
            session.execute(
                update(User).where(User.id == user.id).values(role_id=role.id)
            )

        return True

    @classmethod
    def reset_role(cls, user_id: UUID, default=False) -> bool:
        user = User.find_by_uuid(user_id)
        if not user:
            return False

        with session_scope() as session:
            if default:
                role_id = Role.fetch_default_role()
                session.execute(
                    update(User).where(User.id == user_id).values(role_id=role_id)
                )
            else:
                session.execute(
                    update(User).where(User.id == user_id).values(role_id=None)
                )

        return True

    @classmethod
    def reset_active_tokens(cls, user_id: UUID) -> None:
        jwt_redis_blocklist = get_redis()
        jwt_redis_blocklist.set(
            f"{user_id}:changed-password",
            str(datetime.datetime.now()),
            ex=current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES"),
        )

    @classmethod
    def generate_login(cls, email: Optional[str] = None) -> str:
        if email:
            login, _ = email.split("@")
            return login
        return cls.generate_password(8)

    @classmethod
    def generate_email(cls, social_name: str, login: Optional[str] = None) -> str:
        if login:
            return f"{login}@{social_name}"
        return f"{cls.generate_password(8)}@{social_name}"

    @classmethod
    def generate_password(cls, length: int = 16) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(choice(alphabet) for _ in range(length))

    @classmethod
    def get_user_info(cls, user_id: UUID):
        if user := User.find_by_uuid(user_id):
            return user
        return None

    @classmethod
    def update_subscription(
        cls,
        user_id: UUID,
        expire_date: datetime.datetime,
        is_active: bool,
        subscription_name: Optional[str] = None,
    ):
        user = User.find_by_uuid(user_id)
        with session_scope() as session:
            user.subscription.name = subscription_name or user.subscription.name
            user.subscription.is_active = is_active
            user.subscription.expires_at = expire_date
            session.add(user)
            session.commit()
