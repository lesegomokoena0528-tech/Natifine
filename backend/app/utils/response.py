from flask import jsonify


class ApiResponse:

    @staticmethod
    def success(message, data=None, status=200):

        return jsonify({

            "success": True,

            "message": message,

            "data": data

        }), status

    @staticmethod
    def error(message, status=400, errors=None):

        return jsonify({

            "success": False,

            "message": message,

            "errors": errors

        }), status


# ----------------------------------------
# Convenience Functions
# ----------------------------------------

def success_response(message, data=None, status=200):

    return ApiResponse.success(

        message=message,

        data=data,

        status=status

    )


def error_response(message, status=400, errors=None):

    return ApiResponse.error(

        message=message,

        status=status,

        errors=errors

    )