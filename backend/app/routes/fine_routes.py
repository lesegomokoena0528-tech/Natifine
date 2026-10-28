from flask import Blueprint

from app.controllers.fine_controller import FineController

from app.middleware.auth import login_required
from app.middleware.roles import roles_required

from app.constants.roles import Roles

fine_bp = Blueprint(
    "fines",
    __name__,
    url_prefix="/api/v1/fines"
)

# ==========================================================
# ADMIN & OFFICER
# ==========================================================

fine_bp.route(
    "",
    methods=["POST"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            FineController.issue_fine
        )
    )
)

fine_bp.route(
    "",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            FineController.list_fines
        )
    )
)

fine_bp.route(
    "/search",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            FineController.search
        )
    )
)

fine_bp.route(
    "/statistics",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            FineController.statistics
        )
    )
)

fine_bp.route(
    "/history/<int:fine_id>",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            FineController.history
        )
    )
)

fine_bp.route(
    "/<int:fine_id>",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            FineController.fine_details
        )
    )
)

fine_bp.route(
    "/<int:fine_id>",
    methods=["PUT"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            FineController.update_fine
        )
    )
)

fine_bp.route(
    "/<int:fine_id>/cancel",
    methods=["PATCH"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            FineController.cancel_fine
        )
    )
)

fine_bp.route(
    "/<int:fine_id>/status",
    methods=["PATCH"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value,
            Roles.OFFICER.value
        )(
            FineController.change_status
        )
    )
)

# ==========================================================
# ADMIN ONLY
# ==========================================================

fine_bp.route(
    "/<int:fine_id>",
    methods=["DELETE"]
)(
    login_required(
        roles_required(
            Roles.ADMIN.value
        )(
            FineController.delete_fine
        )
    )
)

# ==========================================================
# CITIZEN
# ==========================================================

fine_bp.route(
    "/my",
    methods=["GET"]
)(
    login_required(
        roles_required(
            Roles.CITIZEN.value
        )(
            FineController.my_fines
        )
    )
)