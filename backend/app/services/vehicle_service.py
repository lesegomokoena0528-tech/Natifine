from app.config.database import db

from app.models.user import (
    UserRole,
    UserStatus
)

from app.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType
)

from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.user_repository import UserRepository

from app.exceptions.vehicle_exceptions import *

from flask_jwt_extended import get_jwt_identity

class VehicleService:

    def __init__(self):

        self.vehicle_repository = VehicleRepository()

        self.user_repository = UserRepository()

    # =====================================================
    # REGISTER VEHICLE
    # =====================================================

    def register_vehicle(self, data):

        registration = data["registration_number"].upper().strip()

        if self.vehicle_repository.exists_registration(
                registration):

            raise DuplicateRegistrationException(
                "Registration number already exists."
            )

        if self.vehicle_repository.exists_vin(
                data["vin"]):

            raise DuplicateVINException(
                "VIN already exists."
            )

        if data.get("engine_number"):

            if self.vehicle_repository.exists_engine_number(
                    data["engine_number"]):

                raise DuplicateEngineNumberException(
                    "Engine number already exists."
                )

        current_user_id = get_jwt_identity()
        current_user = self.user_repository.find_by_id(current_user_id)

        target_owner_id = str(data.get("owner_id")) if data.get("owner_id") else current_user_id

        # If citizen, they can only register a vehicle for themselves
        if current_user and current_user.role == UserRole.CITIZEN:
            target_owner_id = current_user.user_id

        owner = self.user_repository.find_by_id(target_owner_id)

        if not owner:
            raise InvalidVehicleOwnerException(
                "Owner does not exist."
            )

        if owner.status != UserStatus.ACTIVE:
            raise InvalidVehicleOwnerException(
                "Owner account is inactive."
            )

        if owner.role != UserRole.CITIZEN:
            raise InvalidVehicleOwnerException(
                "Only citizens can own vehicles."
            )

        vehicle = Vehicle()

        vehicle.registration_number = registration

        vehicle.owner_id = owner.user_id

        vehicle.make = data["make"]

        vehicle.model = data["model"]

        vehicle.year = data["year"]

        vehicle.color = data.get("color")

        vehicle.vin = data["vin"]

        vehicle.engine_number = data.get("engine_number")

        vehicle.vehicle_type = VehicleType[
            data["vehicle_type"].upper()
        ]

        vehicle.status = VehicleStatus.ACTIVE

        return self.vehicle_repository.save(vehicle)
    
    # =====================================================
    # UPDATE
    # =====================================================

    def update_vehicle(self, vehicle_id, data):

        vehicle = self.vehicle_repository.find_by_id(
            vehicle_id
        )

        if not vehicle:

            raise VehicleNotFoundException()

        if "make" in data:
            vehicle.make = data["make"]

        if "model" in data:
            vehicle.model = data["model"]

        if "year" in data:
            vehicle.year = data["year"]

        if "color" in data:
            vehicle.color = data["color"]

        if "status" in data:
            vehicle.status = VehicleStatus[
                data["status"].upper()
            ]

        if "vehicle_type" in data:
            vehicle.vehicle_type = VehicleType[
                data["vehicle_type"].upper()
            ]

        self.vehicle_repository.update()

        return vehicle
    
    # =====================================================
    # DETAILS
    # =====================================================

    def vehicle_details(self, vehicle_id):

        vehicle = self.vehicle_repository.find_by_id(
            vehicle_id
        )

        if not vehicle:

            raise VehicleNotFoundException()

        return vehicle

    # =====================================================
    # SEARCH
    # =====================================================

    def search(self, keyword):

        return self.vehicle_repository.search(
            keyword
        )
        
    # =====================================================
    # OWNER VEHICLES
    # =====================================================

    def citizen_vehicles(self, owner_id):

        return self.vehicle_repository.find_active_by_owner(
            owner_id
        )
    # =====================================================
    # TRANSFER OWNERSHIP
    # =====================================================

    def change_owner(

        self,

        vehicle_id,

        owner_id

    ):

        vehicle = self.vehicle_repository.find_by_id(
            vehicle_id
        )

        if not vehicle:

            raise VehicleNotFoundException()

        owner = self.user_repository.find_by_id(
            owner_id
        )

        if not owner:

            raise InvalidVehicleOwnerException()

        if owner.role != UserRole.CITIZEN:

            raise InvalidVehicleOwnerException(
                "Owner must be a citizen."
            )

        if owner.status != UserStatus.ACTIVE:

            raise InvalidVehicleOwnerException(
                "Owner account inactive."
            )

        vehicle.owner_id = owner.user_id

        self.vehicle_repository.update()

        return vehicle
    
    # =====================================================
    # DELETE
    # =====================================================

    def delete_vehicle(self, vehicle_id):

        vehicle = self.vehicle_repository.find_by_id(
            vehicle_id
        )

        if not vehicle:

            raise VehicleNotFoundException()

        self.vehicle_repository.delete(vehicle)

        return True
    
    # =====================================================
    # PAGINATION
    # =====================================================

    def list_vehicles(

            self,

            page,

            size

    ):

        return self.vehicle_repository.paginate(
            page,
            size
        )

    # =====================================================
    # VEHICLE HISTORY
    # =====================================================

    def vehicle_history(self, vehicle_id):

        vehicle = self.vehicle_repository.find_by_id(
            vehicle_id
        )

        if not vehicle:

            raise VehicleNotFoundException()

        return [

            fine.to_dict()

            for fine in vehicle.traffic_fines

        ]

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self):

        return {

            "total":

                self.vehicle_repository.count_all(),

            "active":

                self.vehicle_repository.count_active(),

            "stolen":

                self.vehicle_repository.count_stolen(),

            "scrapped":

                self.vehicle_repository.count_scrapped()

        }