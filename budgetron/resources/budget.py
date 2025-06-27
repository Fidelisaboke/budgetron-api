from datetime import datetime

from flask import request, g
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort
from marshmallow import ValidationError

from budgetron.models import Budget, User
from budgetron.schemas import BudgetSchema
from budgetron.utils.db import db
from budgetron.utils.permissions import is_owner_or_admin
from budgetron.utils.paginate import paginate_query

budget_schema = BudgetSchema()
budgets_schema = BudgetSchema(many=True)


class BudgetListResource(Resource):
    @jwt_required()
    def get(self):
        """List all budgets."""
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        query = Budget.query

        # Optional budget filters
        month = request.args.get('month')
        min_amount = request.args.get('min_amount')
        max_amount = request.args.get('max_amount')

        if not g.user.is_admin:
            query = query.filter_by(user_id=g.user.id).all()

        if month:
            try:
                month_date = datetime.fromisoformat(month)
                query = query.filter_by(month=month_date)
            except ValueError:
                return abort(400, message="Invalid month date format. Use the format (YYYY-MM).")

        if min_amount:
            query = query.filter(Budget.amount >= min_amount)

        if max_amount:
            query = query.filter(Budget.amount <= max_amount)

        # Order by budget month
        query = query.order_by(Budget.month.desc())
        budgets = paginate_query(query, budgets_schema, page, limit)

        return budgets, 200

    @jwt_required()
    def post(self):
        """Create a new budget."""
        try:
            data = request.get_json()
            budget_data = budget_schema.load(data)

            existing = Budget.query.filter_by(
                user_id=budget_data['user_id'],
                category_id=budget_data['category_id'],
                month=budget_data['month']
            ).first()

            if existing:
                return {"error": "Budget already exists for this category and month."}, 400
            
            new_budget = Budget(**budget_data)
            db.session.add(new_budget)
            db.session.commit()

            return budget_schema.dump(new_budget), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400


class BudgetDetailResource(Resource):
    @jwt_required()
    @is_owner_or_admin(Budget, id_kwarg="budget_id", object_arg="budget")
    def get(self, budget):
        """Get a single budget."""
        return budget_schema.dump(budget), 200
    
    @jwt_required()
    @is_owner_or_admin(Budget, id_kwarg="budget_id", object_arg="budget")
    def patch(self, budget):
        """Partially update a single budget."""
        try:
            data = request.get_json()
            budget_data = budget_schema.load(data,  partial=True)

            if "user_id" in budget_data:
                existing = User.query.filter_by(user_id=budget_data["user_id"])
                if not existing:
                    abort(404, message="User not found.")
                budget.user_id = budget_data["user_id"]

            if "category_id" in budget_data:
                existing = User.query.filter_by(category_id=budget_data["category_id"])
                if not existing:
                    abort(404, message="Category not found.")
                budget.category_id = budget_data["category_id"]

            if "month" in budget_data:
                budget.month = budget_data["month"]

            if "amount" in budget_data:
                budget.amount = budget_data["amount"]

            db.session.commit()
            return budget_schema.dump(budget), 200
        
        except ValidationError as err:
            return {"errors": err.messages}, 400
        

    @jwt_required()
    @is_owner_or_admin(Budget, id_kwarg="budget_id", object_arg="budget")
    def delete(self, budget):
        """Delete a single budget."""
        db.session.delete(budget)
        db.session.commit()
        return "", 204
