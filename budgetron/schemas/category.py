from marshmallow import Schema, fields, validates, ValidationError, validate

from budgetron.models import Category


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    type = fields.String(required=True, validate=validate.OneOf(["income", "expense"]))
    is_default = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    current_user_id = None
    is_admin = False

    @validates('name')
    def validate_unique_name(self, name, data_key):
        """
        Ensure name is unique per user (or globally if admin/default).
        """
        if self.is_admin:
            # Admins create default categories (user_id = None)
            existing = Category.query.filter_by(name=name, user_id=None).first()
        else:
            # Normal users: check uniqueness against their own categories + defaults
            existing = Category.query.filter_by(name=name).filter(
                (Category.user_id == self.current_user_id) | (Category.user_id is None)
            ).first()

        if existing:
            raise ValidationError("Category name already exists.")