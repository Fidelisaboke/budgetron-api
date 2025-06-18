from marshmallow import Schema, fields, validates, ValidationError, validate

from budgetron.models import User


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=30),
            validate.Regexp(r"[a-zA-Z0-9_]+$", error="Username must be alphanumeric.")
        ]
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, max=255, error="Password must be at least 8 characters long.")
    )
    created_at = fields.DateTime(dump_only=True)

    @validates('username')
    def validate_unique_username(self, username, data_key):
        if User.query.filter_by(username=username).first():
            raise ValidationError("Username is already taken.")

    @validates('email')
    def validate_unique_email(self, email, data_key):
        if User.query.filter_by(email=email).first():
            raise ValidationError("Email is already taken.")


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    type = fields.String(required=True)
    last_updated = fields.DateTime(dump_only=True)


class TransactionSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    amount = fields.Float(required=True)
    type = fields.String(required=True)
    description = fields.String(required=True)
    timestamp = fields.DateTime(dump_only=True)


class ReportSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    format = fields.String(required=True)
    file_url = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
