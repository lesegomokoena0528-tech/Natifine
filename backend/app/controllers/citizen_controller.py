from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService
from app.repositories.citizen_repository import CitizenRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.fine_repository import FineRepository

from app.utils.response import ApiResponse

service = AuthService()
citizen_repo = CitizenRepository()
vehicle_repo = VehicleRepository()
fine_repo = FineRepository()


class CitizenController:

    @staticmethod
    @jwt_required()
    def dashboard():

        user = service.current_user()
        owner_id = user.user_id
        summary = citizen_repo.dashboard_summary(owner_id)
        vehicles = citizen_repo.get_vehicles(owner_id)
        fines = citizen_repo.get_fines(owner_id)[:10]

        return ApiResponse.success(

            "Dashboard",

            {
                "user": user.to_dict(),
                "summary": summary,
                "vehicles": [v.to_dict() for v in vehicles],
                "recent_fines": [f.to_dict() for f in fines],
                "message": "Welcome to NatiFine."
            }

        )