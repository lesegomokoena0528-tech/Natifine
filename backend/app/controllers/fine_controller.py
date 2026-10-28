from flask import request

from marshmallow import ValidationError

from flask_jwt_extended import get_jwt_identity

from app.services.fine_service import FineService

from app.schemas.fine_schema import (
    FineRegistrationSchema,
    FineUpdateSchema,
    FineStatusSchema
)

from app.utils.response import ApiResponse

from app.exceptions.fine_exceptions import *

service = FineService()


from flasgger import swag_from

@staticmethod
@swag_from({
    "tags": ["Traffic Fines"],

    "summary": "Issue Traffic Fine",

    "description": "Creates a new traffic fine.",

    "security": [
        {
            "BearerAuth": []
        }
    ],

    "requestBody": {

        "required": True,

        "content": {

            "application/json": {

                "schema": {

                    "type": "object",

                    "properties": {

                        "vehicle_id": {
                            "type": "integer"
                        },

                        "offence_code": {
                            "type": "string"
                        },

                        "offence": {
                            "type": "string"
                        },

                        "severity": {
                            "type": "string"
                        },

                        "amount": {
                            "type": "number"
                        },

                        "location": {
                            "type": "string"
                        }

                    }

                }

            }

        }

    },

    "responses": {

        "201": {

            "description": "Fine issued successfully"

        },

        "400": {

            "description": "Validation error"

        },

        "401": {

            "description": "Unauthorized"

        },

        "403": {

            "description": "Forbidden"

        }

    }

})
def issue_fine():
    ...


class FineController:

    # ==========================================================
    # ISSUE FINE
    # ==========================================================

    @staticmethod
    def issue_fine():

        try:

            data = FineRegistrationSchema().load(
                request.get_json()
            )

            fine = service.issue_fine(
                data,
                get_jwt_identity()
            )

            return ApiResponse.success(
                "Fine issued successfully.",
                fine.to_dict(),
                201
            )

        except ValidationError as ex:

            return ApiResponse.error(
                ex.messages,
                400
            )

        except FineException as ex:

            return ApiResponse.error(
                str(ex),
                400
            )

        except Exception:

            return ApiResponse.error(
                "Internal server error.",
                500
            )

    # ==========================================================
    # UPDATE FINE
    # ==========================================================

    @staticmethod
    def update_fine(fine_id):

        try:

            data = FineUpdateSchema().load(
                request.get_json(),
                partial=True
            )

            fine = service.update_fine(
                fine_id,
                data
            )

            return ApiResponse.success(
                "Fine updated successfully.",
                fine.to_dict()
            )

        except ValidationError as ex:

            return ApiResponse.error(
                ex.messages,
                400
            )

        except FineException as ex:

            return ApiResponse.error(
                str(ex),
                404
            )

    # ==========================================================
    # FINE DETAILS
    # ==========================================================

    @staticmethod
    def fine_details(fine_id):

        try:

            fine = service.repository.find_by_id(
                fine_id
            )

            if not fine:

                raise FineNotFoundException()

            return ApiResponse.success(
                "Fine retrieved.",
                fine.to_dict()
            )

        except FineException as ex:

            return ApiResponse.error(
                str(ex),
                404
            )

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete_fine(fine_id):

        try:

            fine = service.repository.find_by_id(
                fine_id
            )

            if not fine:

                raise FineNotFoundException()

            service.repository.delete(fine)

            return ApiResponse.success(
                "Fine deleted successfully."
            )

        except FineException as ex:

            return ApiResponse.error(
                str(ex),
                404
            )

    # ==========================================================
    # CANCEL
    # ==========================================================

    @staticmethod
    def cancel_fine(fine_id):

        try:

            data = request.get_json()

            fine = service.cancel_fine(
                fine_id,
                get_jwt_identity(),
                data["reason"]
            )

            return ApiResponse.success(
                "Fine cancelled.",
                fine.to_dict()
            )

        except FineException as ex:

            return ApiResponse.error(
                str(ex),
                400
            )

    # ==========================================================
    # CHANGE STATUS
    # ==========================================================

    @staticmethod
    def change_status(fine_id):

        try:

            data = FineStatusSchema().load(
                request.get_json()
            )

            fine = service.change_status(

                fine_id,

                get_jwt_identity(),

                data["status"],

                data["reason"]

            )

            return ApiResponse.success(
                "Fine status updated.",
                fine.to_dict()
            )

        except ValidationError as ex:

            return ApiResponse.error(
                ex.messages,
                400
            )

        except FineException as ex:

            return ApiResponse.error(
                str(ex),
                400
            )

    # ==========================================================
    # SEARCH
    # ==========================================================

    @staticmethod
    def search():

        keyword = request.args.get(
            "keyword",
            ""
        )

        fines = service.search(keyword)

        return ApiResponse.success(

            "Search completed.",

            [
                fine.to_dict()
                for fine in fines
            ]

        )

    # ==========================================================
    # MY FINES
    # ==========================================================

    @staticmethod
    def my_fines():

        fines = service.citizen_fines(
            get_jwt_identity()
        )

        return ApiResponse.success(

            "Citizen fines retrieved.",

            [
                fine.to_dict()
                for fine in fines
            ]

        )

    # ==========================================================
    # HISTORY
    # ==========================================================

    @staticmethod
    def history(fine_id):

        history = service.history(
            fine_id
        )

        return ApiResponse.success(

            "History retrieved.",

            [
                item.to_dict()
                for item in history
            ]

        )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    @staticmethod
    def statistics():

        return ApiResponse.success(

            "Statistics retrieved.",

            service.statistics()

        )

    # ==========================================================
    # LIST ALL FINES
    # ==========================================================

    @staticmethod
    def list_fines():

        page = request.args.get(
            "page",
            default=1,
            type=int
        )

        size = request.args.get(
            "size",
            default=20,
            type=int
        )

        result = service.repository.paginate(
            page,
            size
        )

        return ApiResponse.success(

            "Fines retrieved.",

            {

                "items": [
                    fine.to_dict()
                    for fine in result.items
                ],

                "page": result.page,

                "pages": result.pages,

                "total": result.total,

                "has_next": result.has_next,

                "has_prev": result.has_prev

            }

        )
        
    # ======================================================
    # CANCEL FINE
    # ======================================================