from flask import request
from flask_restful import Resource, abort
from .models import User, Category, Transaction, Report
from .schemas import UserSchema, CategorySchema, TransactionSchema, ReportSchema
from .utils.db import db

# User Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

class UserResource(Resource):
    def get(self, user_id=None):
        if user_id is None:
            users = User.query.all()
            return users_schema.dump(users), 200

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404, message="User not found.")

        return user_schema.dump(user), 200

    def post(self):
        data = request.get_json()
        user_data = user_schema.load(data)
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()
        return user_schema.dump(new_user), 201

    def patch(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404, message="User not found.")

        data = request.get_json()
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        db.session.commit()
        return user_schema.dump(user), 200

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        if user is None:
            abort(404, message="User not found.")

        db.session.delete(user)
        db.session.commit()
        return "", 204

# Category schema
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
        
class CategoryResource(Resource):
    def get(self, category_id=None):
        if category_id is None:
            categories = Category.query.all()
            return categories_schema.dump(categories), 200

        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404, message="Category not found.")

        return category_schema.dump(category), 200

    def post(self):
        data = request.get_json()
        category_data = category_schema.load(data)
        new_category = Category(**category_data)
        db.session.add(new_category)
        db.session.commit()
        return category_schema.dump(new_category), 201

    def patch(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404, message="Category not found.")

        data = request.get_json()
        category.name = data.get("name", category.name)
        category.type = data.get("type", category.type)
        db.session.commit()
        return category_schema.dump(category), 200

    def delete(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404, message="Category not found.")

        db.session.delete(category)
        db.session.commit()
        return "", 204


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
        data = request.get_json()
        transaction_data = transaction_schema.load(data)
        new_transaction = Transaction(**transaction_data)
        db.session.add(new_transaction)
        db.session.commit()
        return transaction_schema.dump(new_transaction), 201

    def patch(self, transaction_id):
        transaction = Transaction.query.filter_by(id=transaction_id).first()
        if transaction is None:
            abort(404, message="Transaction not found.")

        data = request.get_json()
        transaction.user_id = data.get("user_id", transaction.user_id)
        transaction.category_id = data.get("category_id", transaction.category_id)
        transaction.amount = data.get("amount", transaction.amount)
        transaction.type = data.get("type", transaction.type)
        transaction.description = data.get("description", transaction.description)
        db.session.commit()
        return transaction_schema.dump(transaction), 200

    def delete(self, transaction_id):
        transaction = Transaction.query.filter_by(id=transaction_id).first()
        if transaction is None:
            abort(404, message="Transaction not found.")

        db.session.delete(transaction)
        db.session.commit()
        return "", 204


# Report schema
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)

class ReportResource(Resource):
    def get(self, report_id=None):
        if report_id is None:
            reports = Report.query.all()
            return reports_schema.dump(reports), 200

        report = Report.query.filter_by(id=report_id).first()
        if report is None:
            abort(404, message="Report not found.")

        return report_schema.dump(report), 200

    def post(self):
        data = request.get_json()
        report_data = report_schema.load(data)
        new_report = Report(**report_data)
        db.session.add(new_report)
        db.session.commit()
        return report_schema.dump(new_report), 201

    def patch(self, report_id):
        report = Report.query.filter_by(id=report_id).first()
        if report is None:
            abort(404, message="Report not found.")

        data = request.get_json()
        report.user_id = data.get("user_id", report.user_id)
        report.format = data.get("format", report.format)
        report.file_url = data.get("file_url", report.file_url)
        db.session.commit()
        return report_schema.dump(report), 200

    def delete(self, report_id):
        report = Report.query.filter_by(id=report_id).first()
        if report is None:
            abort(404, message="Report not found.")

        db.session.delete(report)
        db.session.commit()
        return "", 204
