from marshmallow import Schema, fields, validates, ValidationError, validate

from budgetron.models import Category


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    type = fields.String(required=True, validate=validate.OneOf(["income", "expense"]))
    last_updated = fields.DateTime(dump_only=True)

    @validates('name')
    def validate_unique_name(self, name, data_key):
        if Category.query.filter_by(name=name).first():
            raise ValidationError("Category name already exists.")
