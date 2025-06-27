from marshmallow import Schema, fields, validates, ValidationError, validate

from budgetron.models import User


class ReportSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    format = fields.String()
    file_url = fields.String()
    created_at = fields.DateTime(dump_only=True)


class ReportInputSchema(Schema):
    user_id = fields.Integer(required=False)
    month = fields.String(required=True, validate=validate.Regexp(r"\d{4}-\d{2}"))
    format = fields.String(required=True, validate=validate.OneOf(["pdf", "csv", "xlsx"]))

    @validates("user_id")
    def validate_user_id_exists(self, user_id, data_key):
        if user_id and not User.query.filter_by(id=user_id).first():
            raise ValidationError("User not found.")
