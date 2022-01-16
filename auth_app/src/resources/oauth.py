import datetime
from http import HTTPStatus

from flask import current_app, request, url_for
from flask_restful import Resource
from marshmallow import ValidationError

from src.schemas.oauth import OAuthSchema
from src.services.log_history_service import LogHistoryService
from src.services.oauth_service import OAuthService
from src.services.users_service import UserService


class GoogleSignIn(Resource):
    def get(self):
        """
        Google authenticate method.
        ---
        tags:
          - auth
        responses:
          200:
            description: User successfully registered.
          400:
            description: Something went wrong.
        """
        oauth = current_app.extensions["authlib.integrations.flask_client"]
        redirect_uri = url_for("api.googlecallback", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)


class GoogleCallback(Resource):
    oauth_schema = OAuthSchema()

    def get(self):
        oauth = current_app.extensions["authlib.integrations.flask_client"]
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token)

        if user_info:
            generated_password = UserService.generate_password()
            user_data = {
                "email": user_info.get(
                    "email",
                    UserService.generate_email("google", user_info.get("login")),
                ),
                "login": user_info.get(
                    "login", UserService.generate_login(user_info.get("email"))
                ),
                "password": generated_password,
                "social_id": user_info["sub"],
                "social_name": "google",
            }
            try:
                user = self.oauth_schema.load(user_data)
            except ValidationError as e:
                return {"message": str(e)}
            created_user = OAuthService.register(user)
            if not created_user:
                return {"message": "something went wrong"}, HTTPStatus.BAD_REQUEST

            token = OAuthService.login(created_user)
            token["password"] = generated_password

            log_history_data = {
                "logged_at": str(datetime.datetime.utcnow()),
                "user_agent": request.user_agent.string,
                "ip": request.remote_addr,
                "user_id": token["user_id"],
                "refresh_token": token["refresh_token"],
                "expires_at": str(
                    datetime.datetime.utcnow()
                    + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
                ),
            }
            LogHistoryService.create_entry(log_history_data)

            return token, HTTPStatus.OK
        return {"message": "something went wrong"}, HTTPStatus.BAD_REQUEST
