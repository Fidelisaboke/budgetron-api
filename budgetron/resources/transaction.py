from datetime import datetime

from flask import request, g
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort
from marshmallow import ValidationError

from budgetron.models import Transaction, User, Category
from budgetron.schemas import TransactionSchema
from budgetron.utils.db import db
from budgetron.utils.paginate import paginate_query
from budgetron.utils.permissions import is_owner_or_admin

# Transaction schema
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)


class TransactionListResource(Resource):
    @jwt_required()
    def get(self):
        """Lists all transactions."""
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        query = Transaction.query

        # Restrict to current user if not admin
        if not g.user.is_admin:
            query = query.filter_by(user_id=g.user.id)

        # Optional transaction filters
        category_id = request.args.get('category_id', type=int)
        transaction_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_amount = request.args.get('min_amount', type=float)
        max_amount = request.args.get('max_amount', type=float)
        search = request.args.get('search', type=str)

        if category_id:
            query = query.filter_by(category_id=category_id)

        if transaction_type:
            query = query.join(Transaction.category).filter_by(type=transaction_type)

        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                query = query.filter(Transaction.timestamp >= start)
            except ValueError:
                return abort(400, message="Invalid start date format. Use ISO format (YYYY-MM-DD).")

        if end_date:
            try:
                end = datetime.fromisoformat(end_date)
                query = query.filter(Transaction.timestamp <= end)
            except ValueError:
                return abort(400, message="Invalid end date format. Use ISO format (YYYY-MM-DD).")

        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)

        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)

        if search:
            query = query.filter(Transaction.description.ilike(f'%{search}%'))

        # Sort by timestamp descending
        query = query.order_by(Transaction.timestamp.desc())

        transactions = paginate_query(query=query, schema=transactions_schema, page=page, limit=limit)
        return transactions, 200

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
