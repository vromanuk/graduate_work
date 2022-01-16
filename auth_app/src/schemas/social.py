from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from src.database.models import SocialAccount


class SocialAccountSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SocialAccount
        load_instance = True
        include_fk = True
