import click
from flask import current_app
from flask.cli import with_appcontext
from marshmallow import ValidationError
from src.database.db import session_scope
from src.schemas.users import UserSchema
from src.services.auth_service import AuthService


@click.command(name="create-default-user")
@click.argument("login")
@click.argument("password")
@with_appcontext
def create_default_user(login: str, password: str):
    with session_scope() as session:
        try:
            data = {"login": login, "password": password}
            user = UserSchema().load(data, session=session)
        except ValidationError:
            raise click.ClickException("Invalid arguments.")
        AuthService.register(user)
        current_app.logger.info(f"User successfully created")
