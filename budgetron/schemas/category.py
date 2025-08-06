from marshmallow import Schema, fields, validates, ValidationError, validate

from budgetron.models import Category


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    type = fields.String(required=True, validate=validate.OneOf(["income", "expense"]))
    is_default = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('name')
    def validate_unique_name(self, name, data_key):
        user_id = self.context.get('user_id')
        existing = Category.query.filter_by(name=name, user_id=user_id).first()
        if existing:
            raise ValidationError("Category name already exists.")
