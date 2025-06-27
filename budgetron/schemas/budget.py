from marshmallow import Schema, fields, validate, validates, ValidationError
from sqlalchemy import func

from budgetron.models import User, Category, Transaction
from budgetron.utils.db import db


class BudgetSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    month = fields.String(
        required=True,
        validate=validate.Regexp(
            r'^\d{4}-\d{2}$',
            error="Invalid month date format. Use YYYY-MM."
        ),
    )
    amount = fields.Float(required=True)
    spent = fields.Method("get_spent", dump_only=True)
    remaining = fields.Method("get_remaining", dump_only=True)
    overspent = fields.Method("get_overspent", dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    def get_spent(self, obj):
        """
        Return the total amount spent by a user in a category for a given month.
        Assumes `month` is in 'YYYY-MM' format.
        """
        return (
                db.session.query(func.sum(Transaction.amount)).join(Category).filter(
                    Transaction.user_id == obj.user_id,
                    Transaction.category_id == obj.category_id,
                    func.strftime('%Y-%m', Transaction.timestamp) == obj.month,
                    Category.type == 'expense',
                ).scalar() or 0.0
        )

    def get_remaining(self, obj):
        return obj.amount - self.get_spent(obj)

    def get_overspent(self, obj):
        return self.get_spent(obj) > obj.amount

    @validates('user_id')
    def validate_user_id_exists(self, user_id, data_key):
        if User.query.filter_by(id=user_id).first() is None:
            raise ValidationError("User does not exist.")

    @validates('category_id')
    def validate_category_id_exists(self, category_id, data_key):
        if Category.query.filter_by(id=category_id).first() is None:
            raise ValidationError("Category does not exist.")
