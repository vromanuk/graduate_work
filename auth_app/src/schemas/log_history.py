from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from src.database.models import LogHistory


class LogHistorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = LogHistory
        load_instance = True
        include_fk = True
