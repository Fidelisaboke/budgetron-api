from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from budgetron.models import User
from budgetron.schemas import UserSchema
from budgetron.utils.db import db

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UserResource(Resource):
    @jwt_required()
    def get(self, user_id=None):
        if user_id is None:
            users = User.query.all()
            return users_schema.dump(users), 200

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404, message="User not found.")

        return user_schema.dump(user), 200

    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            user_data = user_schema.load(data)

            new_user = User()
            new_user.username = user_data['username']
            new_user.email = user_data['email']
            new_user.set_password(user_data['password'])

            db.session.add(new_user)
            db.session.commit()

            return user_schema.dump(new_user), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400

        except IntegrityError:
            db.session.rollback()
            return {"error": "Username or email already exists."}, 409

    @jwt_required()
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

            if "password" in user_data:
                user.set_password(user_data['password'])

            db.session.commit()
            return user_schema.dump(user), 200

        except ValidationError as err:
            return {"errors": err.messages}, 400

        except IntegrityError:
            db.session.rollback()
            return {"error": "An error occurred when saving user details."}, 409

    @jwt_required()
    def delete(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404, message="User not found.")

        db.session.delete(user)
        db.session.commit()
        return "", 204
