from flask_jwt_extended import JWTManager

from app.utils.response import ApiResponse


def configure_jwt(jwt: JWTManager):

    @jwt.expired_token_loader
    def expired(jwt_header, jwt_payload):

        return ApiResponse.error(

            "Token has expired.",

            401

        )


    @jwt.invalid_token_loader
    def invalid(error):

        return ApiResponse.error(

            "Invalid token.",

            401

        )


    @jwt.unauthorized_loader
    def missing(error):

        return ApiResponse.error(

            "Authorization token required.",

            401

        )


    @jwt.revoked_token_loader
    def revoked(jwt_header, jwt_payload):

        return ApiResponse.error(

            "Token has been revoked.",

            401

        )