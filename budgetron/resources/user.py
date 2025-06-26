from flask import request
from flask_restful import Resource, abort
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from budgetron.models import User, Role
from budgetron.schemas import UserSchema
from budgetron.utils.db import db
from budgetron.utils.jwt import roles_required
from budgetron.utils.paginate import paginate_query

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UserListResource(Resource):
    @roles_required('admin')
    def get(self):
        """Gets all users."""
        page = request.args.get('page', type=int)
        limit = request.args.get('limit', type=int)
        query = User.query.order_by(User.created_at.desc())

        users = paginate_query(query, users_schema, page, limit)
        return users, 200

    @roles_required('admin')
    def post(self):
        try:
            data = request.get_json()
            user_data = user_schema.load(data)

            new_user = User()
            new_user.username = user_data['username']
            new_user.email = user_data['email']
            new_user.set_password(user_data['password'])

            role_names = user_data['roles']
            user_roles = Role.query.filter(Role.name.in_(role_names)).all()
            if len(user_roles) != len(set(role_names)):
                return {'error': 'One or more roles are invalid.'}, 404
            new_user.roles = user_roles

            db.session.add(new_user)
            db.session.commit()

            return user_schema.dump(new_user), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400

        except IntegrityError:
            db.session.rollback()
            return {"error": "Username or email already exists."}, 409


class UserDetailResource(Resource):
    @roles_required('admin')
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404, message="User not found.")

        return user_schema.dump(user), 200

    @roles_required('admin')
    def patch(self, user_id):
        try:
            user = User.query.filter_by(id=user_id).first()
            if user is None:
                abort(404, message="User not found.")

            data = request.get_json()
            user_data = user_schema.load(data, partial=True)

            if "username" in user_data:
                username = user_data["username"]
                existing = User.query.filter(User.username == username, User.id != user.id).first()
                if existing:
                    return {"error": "Username already exists."}, 409
                user.username = username

            if "email" in user_data:
                email = user_data["email"]
                existing = User.query.filter(User.email == email, User.id != user.id).first()
                if existing:
                    return {"error": "Email already exists."}, 409
                user.email = email

            if "roles" in user_data:
                role_names = user_data["roles"]
                roles = Role.query.filter(Role.name.in_(role_names)).all()
                if roles is None or len(roles) != len(role_names):
                    return {"error": "One or more roles are invalid."}, 404
                user.roles = roles

            if "password" in user_data:
                user.set_password(user_data['password'])

            db.session.commit()
            return user_schema.dump(user), 200

        except ValidationError as err:
            return {"errors": err.messages}, 400

        except IntegrityError:
            db.session.rollback()
            return {"error": "An error occurred when saving user details."}, 409

    @roles_required('admin')
    def delete(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404, message="User not found.")

        db.session.delete(user)
        db.session.commit()
        return "", 204
