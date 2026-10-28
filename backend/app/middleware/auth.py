from functools import wraps

from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity
)

from app.repositories.user_repository import UserRepository

repository = UserRepository()


def current_user():

    verify_jwt_in_request()

    user_id = get_jwt_identity()

    user = repository.find_by_id(user_id)

    if not user:
        raise Exception("Authenticated user not found.")

    return user


def login_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()

        return fn(*args, **kwargs)

    return wrapper