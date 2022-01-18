import os
import pathlib
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

# Find the absolute file path to the top level project directory
basedir = pathlib.Path(__file__).parent
API_V1_STR = "/api/v1/"
SWAGGER_TEMPLATE = {
    "components": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        },
        "security": {"bearerAuth": []},
    }
}
SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": f"{API_V1_STR}docs/apispec_1.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": os.path.join(basedir, "static"),
    "swagger_ui": True,
    "specs_route": f"{API_V1_STR}apidocs/",
}
CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"


class Config:
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True

    SECRET_KEY = os.getenv("SECRET_KEY")

    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 30))
    )
    PROPAGATE_EXCEPTIONS = os.getenv("PROPAGATE_EXCEPTIONS", True)

    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    if not SECRET_KEY:
        raise ValueError("No `SECRET_KEY` set for Flask application")
    if not JWT_SECRET_KEY:
        raise ValueError("No `JWT_SECRET_KEY` set for Flask application")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    pass
