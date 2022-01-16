from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError

from src.database.db import session_scope
from src.database.models import Role, SocialAccount, User
from src.schemas.social import SocialAccountSchema


class OAuthService:
    @classmethod
    def register(cls, oauth_user: dict):
        with session_scope() as session:
            social_user_account = (
                session.query(SocialAccount)
                .where(
                    SocialAccount.social_id == oauth_user["social_id"],
                    SocialAccount.social_name == oauth_user["social_name"],
                )
                .first()
            )
            if social_user_account:
                return social_user_account.user
            try:
                user = User(
                    login=oauth_user["login"],
                    email=oauth_user["email"],
                    password=oauth_user["password"],
                )
                default_role_id = Role.fetch_default_role()
                user.role_id = default_role_id

                session.add(user)
                session.commit()

                social_account_dict = {
                    "user_id": user.id,
                    "social_id": oauth_user["social_id"],
                    "social_name": oauth_user["social_name"],
                }
                social_account = SocialAccountSchema().load(
                    social_account_dict, session=session
                )
                session.add(social_account)
                session.commit()

                return user

            except IntegrityError:
                session.rollback()
                return None

    @classmethod
    def login(cls, user) -> dict:
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
        return token
