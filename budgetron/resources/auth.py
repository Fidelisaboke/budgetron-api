from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from budgetron.schemas import UserSchema, LoginSchema, RegisterSchema
from budgetron.models import User, Role
from budgetron.utils.db import db

login_schema = LoginSchema()
register_schema = RegisterSchema()
user_schema = UserSchema(only=('id', 'username', 'email'))

class LoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            login_data = login_schema.load(data)

            email = login_data['email']
            password = login_data['password']

            user = User.query.filter_by(email=email).first()
            if not user:
                raise ValidationError('Invalid email or password')

            if not user.check_password(password):
                raise ValidationError('Invalid email or password')

            access_token = create_access_token(identity=str(user.id))
            return {'access_token': access_token, 'user': user_schema.dump(user)}, 200

        except ValidationError as err:
            return {"errors": err.messages}, 400


class RegisterResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            register_data = register_schema.load(data)
            default_role = Role.query.filter_by(name='user').first()

            new_user = User(username=register_data['username'], email=register_data['email'])
            new_user.roles.append(default_role)
            new_user.set_password(register_data['password'])

            db.session.add(new_user)
            db.session.commit()

            return {
                'message': "Registration successful. Please proceed to login.",
                'user': user_schema.dump(new_user)
            }, 201

        except ValidationError as err:
            return {"errors": err.messages}, 400

        except IntegrityError:
            db.session.rollback()
            return {"error": "An error occurred when saving user details."}, 409
