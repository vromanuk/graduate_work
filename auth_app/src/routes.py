from flask import Blueprint, Flask
from flask_restful import Api

from src.resources.auth import AuthLogin, AuthLogout, AuthRegister
from src.resources.jwt import TokenRefresh
from src.resources.log_history import LogHistoryResource
from src.resources.oauth import GoogleCallback, GoogleSignIn
from src.resources.roles import RolesResource
from src.resources.smoke import Smoke
from src.resources.users import UserRole, Users


def register_blueprints(app: Flask) -> None:
    api_bp = Blueprint("api", __name__, url_prefix="/auth/api/v1")
    api = Api(api_bp)

    # Auth
    api.add_resource(AuthRegister, "/register", strict_slashes=False)
    api.add_resource(AuthLogin, "/login", strict_slashes=False)
    api.add_resource(AuthLogout, "/logout", strict_slashes=False)

    # LogHistory
    api.add_resource(LogHistoryResource, "/users/log-history", strict_slashes=False)

    # Roles
    api.add_resource(RolesResource, "/roles", "/roles/<int>", strict_slashes=False)

    # Smoke
    api.add_resource(Smoke, "/smoke", strict_slashes=False)

    # JWT
    api.add_resource(TokenRefresh, "/refresh", strict_slashes=False)

    # Users
    api.add_resource(Users, "/users", "/users/<uuid:user_id>", strict_slashes=False)
    api.add_resource(
        UserRole,
        "/users/<uuid:user_id>/role/",
        "/users/<uuid:user_id>/role/<int:role_id>",
        strict_slashes=False,
    )

    # OAuth
    api.add_resource(GoogleSignIn, "/oauth/login", strict_slashes=False)
    api.add_resource(GoogleCallback, "/oauth/callback", strict_slashes=False)

    app.register_blueprint(api_bp)
