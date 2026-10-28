from flask import Blueprint

from app.controllers.vehicle_controller import VehicleController

from app.middleware.auth import login_required
from app.middleware.roles import roles_required

from app.constants.roles import Roles

vehicle_bp = Blueprint(
    "vehicles",
    __name__,
    url_prefix="/api/vehicles"
)

# ======================================================
# ADMIN & OFFICER
# ======================================================

vehicle_bp.route(
    "",
    methods=["POST"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value,
            Roles.CITIZEN.value
        )(
            VehicleController.register_vehicle
        )
    )
)

vehicle_bp.route(
    "",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            VehicleController.list_vehicles
        )
    )
)

vehicle_bp.route(
    "/search",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            VehicleController.search
        )
    )
)

vehicle_bp.route(
    "/owners",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            VehicleController.owners
        )
    )
)

vehicle_bp.route(
    "/statistics",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value
        )(
            VehicleController.statistics
        )
    )
)

vehicle_bp.route(
    "/history/<int:vehicle_id>",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            VehicleController.history
        )
    )
)

vehicle_bp.route(
    "/<int:vehicle_id>",
    methods=["PUT"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            VehicleController.update_vehicle
        )
    )
)

vehicle_bp.route(
    "/<int:vehicle_id>/owner",
    methods=["PATCH"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            VehicleController.change_owner
        )
    )
)

# ======================================================
# ADMIN ONLY
# ======================================================

vehicle_bp.route(
    "/<int:vehicle_id>",
    methods=["DELETE"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value
        )(
            VehicleController.delete_vehicle
        )
    )
)

# ======================================================
# ALL AUTHENTICATED USERS
# ======================================================

vehicle_bp.route(
    "/<int:vehicle_id>",
    methods=["GET"]
)(
    login_required(
        VehicleController.vehicle_details
    )
)

# ======================================================
# CITIZENS
# ======================================================

vehicle_bp.route(
    "/my",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.CITIZEN.value
        )(
            VehicleController.my_vehicles
        )
    )
)