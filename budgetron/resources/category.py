from flask import request
from flask_restful import Resource, abort
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from budgetron.models import Category
from budgetron.schemas import CategorySchema
from budgetron.utils.db import db
from budgetron.utils.jwt import roles_required
from budgetron.utils.paginate import paginate_query

# Category schema
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


class CategoryListResource(Resource):
    @jwt_required()
    def get(self):
        """List all categories."""
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        query = Category.query

        # Optional category filters
        category_type = request.args.get('type')

        if category_type:
            query = query.filter_by(type=category_type)

        categories = paginate_query(query, categories_schema, page, limit)
        return categories, 200

    @roles_required('admin')
    def post(self):
        """Creates a new transaction."""
        try:
            data = request.get_json()
            category_data = category_schema.load(data)
            new_category = Category(**category_data)
            db.session.add(new_category)
            db.session.commit()
            return category_schema.dump(new_category), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400


class CategoryDetailResource(Resource):
    @jwt_required()
    def get(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404, message="Category not found.")

        return category_schema.dump(category), 200

    @roles_required('admin')
    def post(self):
        try:
            data = request.get_json()
            category_data = category_schema.load(data)
            new_category = Category(**category_data)
            db.session.add(new_category)
            db.session.commit()
            return category_schema.dump(new_category), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400

    @roles_required('admin')
    def patch(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404, message="Category not found.")

        try:
            data = request.get_json()
            category_data = category_schema.load(data, partial=True)

            if "name" in category_data:
                name = category_data["name"]
                existing = Category.query.filter(Category.name == name, Category.id != category.id).first()
                if existing:
                    return {"error": "Category already exists."}, 409
                category.name = name

            if "type" in category_data:
                category.type = category_data["type"]

            db.session.commit()
            return category_schema.dump(category), 200

        except ValidationError as err:
            return {"errors": err.messages}, 400

    @roles_required('admin')
    def delete(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404, message="Category not found.")

        db.session.delete(category)
        db.session.commit()
        return "", 204
