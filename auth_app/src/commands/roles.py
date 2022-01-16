import click
from flask import current_app
from flask.cli import with_appcontext

from src.database.db import session_scope
from src.database.models import Role


@click.command(name="create-roles")
@with_appcontext
def create_roles():
    Role.insert_roles()
    with session_scope() as session:
        roles = session.query(Role).all()
    current_app.logger.info(f"Roles {roles} has been added")
