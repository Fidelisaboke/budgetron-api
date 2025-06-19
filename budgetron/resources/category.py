from flask import request
from flask_restful import Resource, abort
from marshmallow import ValidationError

from budgetron.models import Category
from budgetron.schemas import CategorySchema
from budgetron.utils.db import db

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
        try:
            data = request.get_json()
            category_data = category_schema.load(data)
            new_category = Category(**category_data)
            db.session.add(new_category)
            db.session.commit()
            return category_schema.dump(new_category), 201
        except ValidationError as err:
            return {"errors": err.messages}, 400

    def patch(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404, message="Category not found.")

        try:
            data = request.get_json()
            category.name = data.get("name", category.name)
            category.type = data.get("type", category.type)
            db.session.commit()
            return category_schema.dump(category), 200
        except ValidationError as err:
            return {"errors": err.messages}, 400

    def delete(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404, message="Category not found.")

        db.session.delete(category)
        db.session.commit()
        return "", 204