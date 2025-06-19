from flask import request
from flask_restful import Resource, abort
from marshmallow import ValidationError

from budgetron.models import Transaction
from budgetron.schemas import TransactionSchema
from budgetron.utils.db import db

# Transaction schema
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)

class TransactionResource(Resource):
    def get(self, transaction_id=None):
        if transaction_id is None:
            transactions = Transaction.query.all()
            return transactions_schema.dump(transactions), 200

        transaction = Transaction.query.filter_by(id=transaction_id).first()
        if transaction is None:
            abort(404, message="Transaction not found.")

        return transaction_schema.dump(transaction), 200

    def post(self):
        try:
            data = request.get_json()
            transaction_data = transaction_schema.load(data)
            new_transaction = Transaction(**transaction_data)
            db.session.add(new_transaction)
            db.session.commit()
            return transaction_schema.dump(new_transaction), 201
        except ValidationError as err:
            return {"errors": err.messages}, 400

    def patch(self, transaction_id):
        transaction = Transaction.query.filter_by(id=transaction_id).first()
        if transaction is None:
            abort(404, message="Transaction not found.")

        try:
            data = request.get_json()
            transaction.user_id = data.get("user_id", transaction.user_id)
            transaction.category_id = data.get("category_id", transaction.category_id)
            transaction.amount = data.get("amount", transaction.amount)
            transaction.description = data.get("description", transaction.description)
            db.session.commit()
            return transaction_schema.dump(transaction), 200
        except ValidationError as err:
            return {"errors": err.messages}, 400

    def delete(self, transaction_id):
        transaction = Transaction.query.filter_by(id=transaction_id).first()
        if transaction is None:
            abort(404, message="Transaction not found.")

        db.session.delete(transaction)
        db.session.commit()
        return "", 204