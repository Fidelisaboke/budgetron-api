from flask import request, g
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort
from marshmallow import ValidationError

from budgetron.models import Transaction, User, Category
from budgetron.schemas import TransactionSchema
from budgetron.utils.db import db
from budgetron.utils.permissions import is_owner_or_admin

# Transaction schema
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)


class TransactionListResource(Resource):
    @jwt_required()
    def get(self):
        """Lists all transactions."""
        if not g.user.is_admin:
            transactions = Transaction.query.filter_by(user_id=g.user.id).all()
            return transactions_schema.dump(transactions), 200

        transactions = Transaction.query.all()
        return transactions_schema.dump(transactions), 200

    @jwt_required()
    def post(self):
        """Creates a new transaction."""
        try:
            data = request.get_json()
            transaction_data = transaction_schema.load(data)
            new_transaction = Transaction(**transaction_data)
            db.session.add(new_transaction)
            db.session.commit()
            return transaction_schema.dump(new_transaction), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400


class TransactionDetailResource(Resource):
    @jwt_required()
    @is_owner_or_admin(Transaction, id_kwarg="transaction_id", object_arg="transaction")
    def get(self, transaction):
        """Gets a single transaction."""
        return transaction_schema.dump(transaction), 200

    @jwt_required()
    @is_owner_or_admin(Transaction, id_kwarg="transaction_id", object_arg="transaction")
    def patch(self, transaction):
        """Partially updates a single transaction."""
        try:
            data = request.get_json()
            transaction_data = transaction_schema.load(data, partial=True)

            if "user_id" in transaction_data:
                existing = User.query.filter_by(id=transaction_data["user_id"]).first()
                if not existing:
                    abort(404, message="User not found.")
                transaction.user_id = transaction_data["user_id"]

            if "category_id" in transaction_data:
                existing = Category.query.filter_by(id=transaction_data["category_id"]).first()
                if not existing:
                    abort(404, message="Category not found.")
                transaction.category_id = transaction_data["category_id"]

            if "amount" in transaction_data:
                transaction.amount = transaction_data["amount"]

            if "description" in transaction_data:
                transaction.description = transaction_data["description"]

            db.session.commit()
            return transaction_schema.dump(transaction), 200

        except ValidationError as err:
            return {"errors": err.messages}, 400

    @jwt_required()
    @is_owner_or_admin(Transaction, id_kwarg="transaction_id", object_arg="transaction")
    def delete(self, transaction):
        """Deletes a transaction."""
        db.session.delete(transaction)
        db.session.commit()
        return "", 204
