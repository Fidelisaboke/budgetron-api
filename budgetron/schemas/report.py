from marshmallow import Schema, fields, validates, ValidationError, validate

from budgetron.models import User


class ReportSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    format = fields.String(required=True, validate=validate.OneOf(["pdf", "csv", "xlsx"]))
    file_url = fields.String(required=True, validate=validate.URL())
    created_at = fields.DateTime(dump_only=True)

    @validates('user_id')
    def validate_user_id_exists(self, user_id, data_key):
        if User.query.filter_by(id=user_id).first() is None:
            raise ValidationError("User does not exist.")
