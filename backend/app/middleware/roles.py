from functools import wraps

from flask_jwt_extended import verify_jwt_in_request

from app.middleware.auth import current_user

from app.utils.response import ApiResponse


def roles_required(*roles):

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            verify_jwt_in_request()

            user = current_user()

            if user.role.value not in roles:

                return ApiResponse.error(

                    "Access denied.",

                    403

                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator