import traceback
from flask import request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required

from app.services.auth_service import AuthService
from app.utils.response import ApiResponse
from app.schemas.user_schemas import RegisterSchema
from app.exceptions.auth_exceptions import *

auth_service = AuthService()


class AuthController:

    @staticmethod
    def register():

        try:
            json_data = request.get_json() or {}
            data = RegisterSchema().load(json_data)

            user = auth_service.register(data)

            return ApiResponse.success(
                "User registered successfully.",
                user.to_dict(),
                201
            )

        except ValidationError as ex:
            return ApiResponse.error(ex.messages, 400)

        except DuplicateUserException as ex:
            return ApiResponse.error(str(ex), 409)

        except Exception as ex:
            return ApiResponse.error(str(ex), 500)

    # ----------------------------------

    @staticmethod
    def login():

        try:
            data = request.get_json() or {}
            username = data.get("username") or data.get("email") or data.get("identifier")
            password = data.get("password")

            if not username or not password:
                return ApiResponse.error(
                    "Username (email/phone/ID) and password are required.",
                    400
                )

            result = auth_service.login(
                username,
                password
            )

            return ApiResponse.success(
                "Login successful.",
                result
            )

        except AuthenticationException as ex:
            return ApiResponse.error(str(ex), 401)

        except AccountLockedException as ex:
            return ApiResponse.error(str(ex), 423)

        except AccountInactiveException as ex:
            return ApiResponse.error(str(ex), 403)

        except Exception as ex:
            traceback.print_exc()
            return ApiResponse.error(str(ex), 500)

    # ----------------------------------

    @staticmethod
    @jwt_required(refresh=True)
    def refresh():

        token = auth_service.refresh()

        return ApiResponse.success(

            "Token refreshed.",

            {

                "access_token": token

            }

        )

    # ----------------------------------

    @staticmethod
    @jwt_required()
    def profile():

        try:
            user = auth_service.current_user()

            return ApiResponse.success(

                "Profile retrieved.",

                user.to_dict()

            )
        except AccountLockedException as ex:
            return ApiResponse.error(str(ex), 401)
        except AccountInactiveException as ex:
            return ApiResponse.error(str(ex), 401)
        except AuthenticationException as ex:
            return ApiResponse.error(str(ex), 401)
        except Exception as ex:
            return ApiResponse.error(str(ex), 500)

    # ----------------------------------

    @staticmethod
    @jwt_required()
    def change_password():

        try:
            data = request.get_json() or {}
            current_pw = data.get("current_password")
            new_pw = data.get("new_password")

            if not current_pw or not new_pw:
                return ApiResponse.error(
                    "Both current_password and new_password are required.",
                    400
                )

            auth_service.change_password(
                current_pw,
                new_pw
            )

            return ApiResponse.success(
                "Password changed successfully."
            )
        except AuthenticationException as ex:
            return ApiResponse.error(str(ex), 401)
        except Exception as ex:
            return ApiResponse.error(str(ex), 500)