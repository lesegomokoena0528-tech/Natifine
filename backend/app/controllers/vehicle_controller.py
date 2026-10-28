from flask import request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.services.vehicle_service import VehicleService

from app.schemas.vehicle_schema import (
    VehicleRegistrationSchema,
    VehicleUpdateSchema
)

from app.repositories.user_repository import UserRepository

from app.utils.response import ApiResponse

from app.exceptions.vehicle_exceptions import *

service = VehicleService()

user_repository = UserRepository()


class VehicleController:

    # ===================================================
    # REGISTER VEHICLE
    # ===================================================

    @staticmethod
    def register_vehicle():

        try:

            data = VehicleRegistrationSchema().load(
                request.get_json()
            )

            vehicle = service.register_vehicle(data)

            return ApiResponse.success(

                "Vehicle registered successfully.",

                vehicle.to_dict(),

                201

            )

        except ValidationError as ex:

            return ApiResponse.error(

                ex.messages,

                400

            )

        except VehicleException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

        except Exception:

            return ApiResponse.error(

                "Internal server error.",

                500

            )

    # ===================================================
    # UPDATE VEHICLE
    # ===================================================

    @staticmethod
    def update_vehicle(vehicle_id):

        try:

            data = VehicleUpdateSchema().load(

                request.get_json(),

                partial=True

            )

            vehicle = service.update_vehicle(

                vehicle_id,

                data

            )

            return ApiResponse.success(

                "Vehicle updated successfully.",

                vehicle.to_dict()

            )

        except ValidationError as ex:

            return ApiResponse.error(

                ex.messages,

                400

            )

        except VehicleException as ex:

            return ApiResponse.error(

                str(ex),

                404

            )

    # ===================================================
    # DELETE VEHICLE
    # ===================================================

    @staticmethod
    def delete_vehicle(vehicle_id):

        try:

            service.delete_vehicle(vehicle_id)

            return ApiResponse.success(

                "Vehicle deleted successfully."

            )

        except VehicleException as ex:

            return ApiResponse.error(

                str(ex),

                404

            )

    # ===================================================
    # VEHICLE DETAILS
    # ===================================================

    @staticmethod
    def vehicle_details(vehicle_id):

        try:

            vehicle = service.vehicle_details(

                vehicle_id

            )

            current_user = user_repository.find_by_id(
                get_jwt_identity()
            )

            if current_user.role.value == "CITIZEN":

                if vehicle.owner_id != current_user.user_id:

                    return ApiResponse.error(

                        "Access denied.",

                        403

                    )

            return ApiResponse.success(

                "Vehicle retrieved.",

                vehicle.to_dict()

            )

        except VehicleException as ex:

            return ApiResponse.error(

                str(ex),

                404

            )

    # ===================================================
    # SEARCH
    # ===================================================

    @staticmethod
    def search():

        keyword = request.args.get(

            "keyword",

            ""

        )

        vehicles = service.search(

            keyword

        )

        return ApiResponse.success(

            "Search completed.",

            [

                vehicle.to_dict()

                for vehicle in vehicles

            ]

        )

    # ===================================================
    # ACTIVE CITIZEN OWNERS
    # ===================================================

    @staticmethod
    def owners():

        keyword = request.args.get(
            "keyword",
            ""
        ).strip().lower()

        owners = []

        for user in user_repository.citizens():

            if user.status.value != "ACTIVE":
                continue

            haystack = " ".join([
                user.full_name or "",
                user.email or "",
                user.id_number or "",
                user.phone or ""
            ]).lower()

            if keyword and keyword not in haystack:
                continue

            owners.append({
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "id_number": user.id_number,
                "phone": user.phone
            })

        return ApiResponse.success(
            "Owners retrieved.",
            owners
        )

    # ===================================================
    # MY VEHICLES
    # ===================================================

    @staticmethod
    def my_vehicles():

        owner_id = get_jwt_identity()

        vehicles = service.citizen_vehicles(

            owner_id

        )

        return ApiResponse.success(

            "Vehicles retrieved.",

            [

                vehicle.to_dict()

                for vehicle in vehicles

            ]

        )

    # ===================================================
    # CHANGE OWNER
    # ===================================================

    @staticmethod
    def change_owner(vehicle_id):

        data = request.get_json()

        vehicle = service.change_owner(

            vehicle_id,

            data["owner_id"]

        )

        return ApiResponse.success(

            "Vehicle owner changed.",

            vehicle.to_dict()

        )

    # ===================================================
    # PAGINATION
    # ===================================================

    @staticmethod
    def list_vehicles():

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

        result = service.list_vehicles(

            page,

            size

        )

        return ApiResponse.success(

            "Vehicles retrieved.",

            {

                "items": [

                    vehicle.to_dict()

                    for vehicle in result.items

                ],

                "page": result.page,

                "pages": result.pages,

                "total": result.total,

                "has_next": result.has_next,

                "has_prev": result.has_prev

            }

        )

    # ===================================================
    # STATISTICS
    # ===================================================

    @staticmethod
    def statistics():

        return ApiResponse.success(

            "Statistics retrieved.",

            service.statistics()

        )

    # ===================================================
    # HISTORY
    # ===================================================

    @staticmethod
    def history(vehicle_id):

        history = service.vehicle_history(

            vehicle_id

        )

        return ApiResponse.success(

            "Vehicle history retrieved.",

            history

        )