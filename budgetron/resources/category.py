from flask import request, g
from flask_restful import Resource, abort
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from budgetron.models import Category, User
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
        """
        List categories.
        - Admins see all categories
        - Users see default + their own
        """
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        category_type = request.args.get('type')
        search_query = request.args.get('search', '', type=str)

        query = Category.query

        # Filter for default or user-owned categories
        if not g.user.is_admin:
            query = query.filter((Category.is_default == True) | (Category.user_id == g.user.id))

        # Type filter
        if category_type and category_type != "all":
            query = query.filter_by(type=category_type)

        # Search filter
        if search_query:
            query = query.filter(Category.name.ilike(f"{search_query}%"))

        categories = paginate_query(query.order_by(Category.name.asc()), categories_schema, page, limit)
        return categories, 200
    

    @jwt_required()
    def post(self):
        """
        Create a category.
        - Admins create global (is_default=True)
        - Users create personal (user_id = g.user.id)
        """
        try:
            data = request.get_json()

            # Load with user_id context to validate per-user uniqueness
            category_data = category_schema.load(data, context={"user_id": g.user.id})


            # Create a new category
            new_category = Category(
                **category_data,
                user_id=None if g.user.is_admin else g.user.id,
                is_default=True if g.user.is_admin else False
            )


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

        # Return 404 if user is not authorized to view category
        if not g.user.is_admin and not (category.is_default or category.user_id == g.user.id):
            abort(404, message="Category not found.")

        return category_schema.dump(category), 200


    @roles_required('admin')
    def patch(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404, message="Category not found.")

        # Return 404 if user is not authorized to update category
        if not g.user.is_admin and category.user_id != g.user.id:
            abort(404, message="Category not found.")

        try:
            data = request.get_json()
            category_data = category_schema.load(data, partial=True)

            if "name" in category_data:
                name = category_data["name"]
                
                # Check for an existing category
                existing = Category.query.filter(
                    Category.name == name,
                    Category.id != category.id,
                    (Category.user_id == g.user.id) | (Category.is_default == True)
                ).first()

                if existing:
                    return {"error": "Category with this name already exists."}, 409
                
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

        # Return 404 if user is not authorized to update category
        if not g.user.is_admin and category.user_id != g.user.id:
            abort(404, message="Category not found.")

        db.session.delete(category)
        db.session.commit()
        return "", 204
