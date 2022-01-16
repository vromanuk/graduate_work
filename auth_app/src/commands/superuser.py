import click
from flask import current_app
from flask.cli import with_appcontext
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from src.database.db import session_scope
from src.database.models import Role
from src.schemas.users import UserSchema


@click.command(name="create-superuser")
@click.argument("login")
@click.argument("password")
@with_appcontext
def create_superuser(login: str, password: str):
    with session_scope() as session:
        try:
            data = {"login": login, "password": password}
            user = UserSchema().load(data, session=session)
        except ValidationError:
            raise click.ClickException("Invalid arguments.")
        try:
            admin_role_id = (
                session.query(Role)
                .filter_by(permissions=0xFF)
                .with_entities(Role.id)
                .scalar()
            )
            user.role_id = admin_role_id
            session.add(user)
            session.commit()
            current_app.logger.info("Superuser successfully created")
        except IntegrityError:
            session.rollback()
            current_app.logger.info("Such user exists")
