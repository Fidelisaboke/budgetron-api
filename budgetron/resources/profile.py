from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from budgetron.models import User
from budgetron.schemas import UserSchema

user_schema = UserSchema()


class ProfileResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return {"error": "User not found."}, 404

        return user_schema.dump(user), 200
