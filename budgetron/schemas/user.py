from marshmallow import Schema, fields, validates, ValidationError, validate

from budgetron.models import User, Role


class BaseUserSchema(Schema):
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=30),
            validate.Regexp(
                r"[a-zA-Z0-9_]+$",
                error="Username can contain numbers, letters, and underscores only."
            )
        ]
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, max=255, error="Password must be at least 8 characters long.")
    )

    @validates('username')
    def validate_unique_username(self, username, data_key):
        if User.query.filter_by(username=username).first():
            raise ValidationError("Username is already taken.")

    @validates('email')
    def validate_unique_email(self, email, data_key):
        if User.query.filter_by(email=email).first():
            raise ValidationError("Email is already taken.")


class UserSchema(BaseUserSchema):
    id = fields.Integer(dump_only=True)
    roles = fields.Method("get_roles", deserialize="load_roles")
    created_at = fields.DateTime(dump_only=True)

    @staticmethod
    def get_roles(obj):
        # Serialize roles as a list of strings
        return [role.name for role in obj.roles]

    @staticmethod
    def load_roles(value):
        # Accept list of strings for deserialization
        return value

    @validates('roles')
    def validate_roles(self, roles_list, data_key):
        existing_roles = {r.name for r in Role.query.all()}
        for role in roles_list:
            if role not in existing_roles:
                raise ValidationError(f"Role '{role}' does not exist.")


class RegisterSchema(BaseUserSchema):
    pass


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
