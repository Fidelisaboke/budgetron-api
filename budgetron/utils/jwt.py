from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from functools import wraps

from flask_restful import abort

from budgetron.models import User

jwt = JWTManager()

@jwt.additional_claims_loader
def add_claims(identity):
    user = User.query.get(int(identity))
    return {
        "roles": [role.name for role in user.roles]
    }

def roles_required(*roles):
    """
    A decorator function that checks that the user has the given roles.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            jwt_roles = get_jwt().get("roles", [])
            if not set(roles).intersection(jwt_roles):
                return abort(403, description="You are not authorized to perform this action.")
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {"msg": "Token has expired"}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"msg": "Invalid token"}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"msg": "Missing Authorization Header"}, 401

@jwt.revoked_token_loader
def revoked_token_callback(error):
    return {"msg": "Token has been revoked"}, 401
