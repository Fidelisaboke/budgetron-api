from functools import wraps
from flask import g
from flask_restful import abort
from sqlalchemy.orm.exc import NoResultFound


def is_owner_or_admin(model, id_kwarg="id", owner_attr="user_id", object_arg="obj"):
    """
    A decorator that checks whether the resource is owned by the user
    making the request.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            instance_id = kwargs.pop(id_kwarg, None)
            obj = model.query.get(instance_id)

            if obj is None:
                abort(404, message=f"{model.__name__} not found.")

            if not g.user.is_admin and getattr(obj, owner_attr) != g.user.id:
                abort(403, message="You are not authorized to access this resource.")

            kwargs[object_arg] = obj
            return fn(*args, **kwargs)

        return decorated

    return wrapper
