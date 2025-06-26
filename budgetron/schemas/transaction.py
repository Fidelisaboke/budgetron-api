from marshmallow import Schema, fields, validates, ValidationError, validate

from budgetron.models import User, Category


class TransactionSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=1))
    description = fields.String(required=True, validate=validate.Length(min=5, max=255))
    timestamp = fields.DateTime(dump_only=True)

    @validates('user_id')
    def validate_user_id_exists(self, user_id, data_key):
        if User.query.filter_by(id=user_id).first() is None:
            raise ValidationError("User does not exist.")

    @validates('category_id')
    def validate_category_id_exists(self, category_id, data_key):
        if Category.query.filter_by(id=category_id).first() is None:
            raise ValidationError("Category does not exist.")
