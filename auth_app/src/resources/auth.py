import datetime
from http import HTTPStatus

import opentracing
from flask import current_app, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError

from src import get_redis
from src.database.db import session_scope
from src.database.models import User
from src.schemas.users import UserSchema
from src.services.auth_service import AuthService
from src.services.log_history_service import LogHistoryService


class AuthRegister(Resource):
    user_schema = UserSchema()
    model = User

    def post(self):
        """
        User register method.
        ---
        tags:
          - auth
        consumes:
          - application/json
        parameters:
        - in: body
          name: user
          description: The user to register.
          schema:
            type: object
            required:
              - login
              - password
            properties:
              login:
                type: string
              password:
                type: string
        responses:
          200:
            description: User successfully registered.
          400:
            description: Invalid data.
          409:
            description: Such user exists.
        """
        flask_tracer = current_app.extensions["flask_tracer"]
        parent_span = flask_tracer.get_span()
        try:
            with session_scope() as session:
                user = self.user_schema.load(request.json, session=session)
        except ValidationError as e:
            return {"message": str(e)}, HTTPStatus.BAD_REQUEST

        with opentracing.tracer.start_span("register", child_of=parent_span) as span:
            span.set_tag("db.call", "register")
            created = AuthService.register(user)
            span.set_tag("db.response", created)
        if created:
            return {"result": self.user_schema.dump(user)}, HTTPStatus.CREATED
        return {"message": "Such user exists"}, HTTPStatus.CONFLICT


class AuthLogin(Resource):
    def post(self):
        """
        User authenticate method.
        ---
        tags:
          - auth
        consumes:
          - application/json
        parameters:
        - in: body
          name: user
          description: The user to authenticate.
          schema:
            type: object
            required:
              - login
              - password
            properties:
              login:
                type: string
              password:
                type: string
        responses:
          200:
            description: User successfully registered.
          401:
            description: Invalid credentials.
        """
        flask_tracer = current_app.extensions["flask_tracer"]
        parent_span = flask_tracer.get_span()
        login = request.json.get("login", None)
        password = request.json.get("password", None)

        with opentracing.tracer.start_span("login", child_of=parent_span) as span:
            span.set_tag("db.call", "login")
            logged_in, token = AuthService.login(login=login, password=password)
            span.set_tag("db.response", logged_in)
        if not logged_in:
            return {"message": "Invalid Credentials."}, HTTPStatus.UNAUTHORIZED

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
        with opentracing.tracer.start_span("log-history", child_of=parent_span) as span:
            span.set_tag("db.call", "log_history")
            LogHistoryService.create_entry(log_history_data)
            span.set_tag("db.response", "ok")

        return token, HTTPStatus.OK


class AuthLogout(Resource):
    @jwt_required()
    def delete(self):
        """
        User logout method.
        ---
        tags:
          - auth
        description: Logout user.
        security:
            - bearerAuth: []
        responses:
          200:
            description: User successfully logged in.
        """
        flask_tracer = current_app.extensions["flask_tracer"]
        parent_span = flask_tracer.get_span()
        with opentracing.tracer.start_span("logout", child_of=parent_span) as span:
            span.set_tag("redis.call", "add-key-to-redis")
            jti = get_jwt()["jti"]
            current_user_id = get_jwt_identity()
            jwt_redis_blocklist = get_redis()
            jwt_redis_blocklist.set(
                f"{current_user_id}:{jti}:{request.user_agent.string}",
                "",
                ex=current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES"),
            )
            span.set_tag(
                "redis.ack", f"{current_user_id}:{jti}:{request.user_agent.string}"
            )
        return {"message": "Access token revoked"}, HTTPStatus.OK
