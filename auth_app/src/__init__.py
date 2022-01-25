import os
import pathlib
from datetime import datetime as dt

import redis
from authlib.integrations.flask_client import OAuth
from flasgger import Swagger
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_opentracing import FlaskTracer
from jaeger_client import Config

from src import config, redis_utils
from src.config import SWAGGER_TEMPLATE
from src.database.db import init_db
from src.redis_utils import get_redis

jwt = JWTManager()
swag = Swagger(template=SWAGGER_TEMPLATE, config=config.SWAGGER_CONFIG)
oauth = OAuth()
limiter = Limiter(
    key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)


def create_app():
    from src.routes import register_blueprints

    app = Flask(__name__, instance_relative_config=True)
    cfg = os.getenv("CONFIG_TYPE", default="src.config.DevelopmentConfig")
    app.config.from_object(cfg)

    app.config.update({"SWAGGER": {"title": "Auth Service", "openapi": "3.0.3"}})

    register_blueprints(app)
    configure_logging(app)
    init_db()
    initialize_extensions(app)
    initialize_commands(app)
    setup_redis(app)
    setup_oauth()

    return app


def initialize_extensions(app) -> None:
    jwt.init_app(app)
    swag.init_app(app)
    oauth.init_app(app)
    limiter.init_app(app)
    flask_tracer = FlaskTracer(initialize_tracer, True, app)
    app.extensions["flask_tracer"] = flask_tracer


def initialize_commands(app) -> None:
    from src.commands.create_default_user import create_default_user
    from src.commands.roles import create_roles
    from src.commands.superuser import create_superuser

    app.cli.add_command(create_superuser)
    app.cli.add_command(create_roles)
    app.cli.add_command(create_default_user)


def configure_logging(app: Flask) -> None:
    import logging
    from logging.handlers import RotatingFileHandler

    from flask.logging import default_handler

    basedir = pathlib.Path(__file__).parent
    logdir = basedir.joinpath("logs")
    if not logdir.exists():
        logdir.mkdir()
    logfile = logdir.joinpath("flaskapp.log")

    # Deactivate the default flask logger so that log messages don't get duplicated
    app.logger.removeHandler(default_handler)
    file_handler = RotatingFileHandler(logfile, maxBytes=16384, backupCount=20)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(filename)s: %(lineno)d]"
    )
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)


def setup_redis(app) -> None:
    redis_utils.redis = redis.StrictRedis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=0,
        decode_responses=True,
    )


def setup_oauth() -> None:
    oauth.register(
        name="google",
        server_metadata_url=config.CONF_URL,
        client_kwargs={"scope": "openid email profile"},
    )


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jwt_redis_blocklist = get_redis()
    logged_in_after_changing_password = False
    jti = jwt_payload["jti"]
    issued_at = dt.fromtimestamp(jwt_payload["iat"])
    current_user_id = jwt_payload["sub"]
    redis_key = f"{current_user_id}:{jti}"
    changed_password_key = f"{current_user_id}:changed-password"

    token_in_redis = jwt_redis_blocklist.get(redis_key)
    has_changed_password = jwt_redis_blocklist.get(changed_password_key)
    if has_changed_password:
        changed_password_at = dt.strptime(has_changed_password, "%Y-%m-%d %H:%M:%S.%f")
        logged_in_after_changing_password = issued_at < changed_password_at

    return token_in_redis is not None or logged_in_after_changing_password


def initialize_tracer():
    jaeger_config = Config(
        config={"sampler": {"type": "const", "param": 1}}, service_name="auth-service"
    )
    return jaeger_config.initialize_tracer()  # also sets opentracing.tracer
