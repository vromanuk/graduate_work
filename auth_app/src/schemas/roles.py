from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from src.database.models import Role


class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        exclude = ["id"]
        load_instance = True
        include_fk = True
