from marshmallow import Schema, fields
from marshmallow.validate import Length


class OAuthSchema(Schema):
    login = fields.Str()
    email = fields.Email()
    password = fields.Str()
    social_id = fields.Str(validate=Length(max=64))
    social_name = fields.Str(validate=Length(max=64))

    # @validates_schema
    # def validate_login_and_email(self, data, **kwargs):
    #     if not data["login"] or data["email"]:
    #         raise ValidationError("you must specify one of these fields: `email` or `login`")
