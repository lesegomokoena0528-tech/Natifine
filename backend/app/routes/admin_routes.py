from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.admin_controller import AdminController
from app.middleware.roles import roles_required

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)

controller = AdminController()

# ==========================================================
# DASHBOARD
# ==========================================================

@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def dashboard():
    return controller.dashboard()


@admin_bp.route("/statistics", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def statistics():
    return controller.statistics()


# ==========================================================
# USER MANAGEMENT
# ==========================================================

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def get_users():
    return controller.get_users()


@admin_bp.route("/users/search", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def search_users():
    return controller.search_users()


@admin_bp.route("/users/<string:user_id>", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def get_user(user_id):
    return controller.get_user(user_id)


@admin_bp.route("/users", methods=["POST"])
@jwt_required()
@roles_required("ADMIN")
def create_user():
    return controller.create_user()


@admin_bp.route("/users/<string:user_id>", methods=["PUT"])
@jwt_required()
@roles_required("ADMIN")
def update_user(user_id):
    return controller.update_user(user_id)


@admin_bp.route("/users/<string:user_id>", methods=["DELETE"])
@jwt_required()
@roles_required("ADMIN")
def delete_user(user_id):
    return controller.delete_user(user_id)


@admin_bp.route("/users/<string:user_id>/activate", methods=["PUT"])
@jwt_required()
@roles_required("ADMIN")
def activate_user(user_id):
    return controller.activate_user(user_id)


@admin_bp.route("/users/<string:user_id>/deactivate", methods=["PUT"])
@jwt_required()
@roles_required("ADMIN")
def deactivate_user(user_id):
    return controller.deactivate_user(user_id)


@admin_bp.route("/users/<string:user_id>/role", methods=["PUT"])
@jwt_required()
@roles_required("ADMIN")
def assign_role(user_id):
    return controller.assign_role(user_id)


@admin_bp.route("/users/<string:user_id>/reset-password", methods=["POST"])
@jwt_required()
@roles_required("ADMIN")
def reset_password(user_id):
    return controller.reset_password(user_id)


# ==========================================================
# OFFICER MANAGEMENT
# ==========================================================

@admin_bp.route("/officers", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def officers():
    return controller.officers()


# ==========================================================
# REPORTS
# ==========================================================

@admin_bp.route("/reports/dashboard", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def dashboard_report():
    return controller.dashboard_report()


@admin_bp.route("/reports/revenue", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def revenue_report():
    return controller.revenue_report()


@admin_bp.route("/reports/fines", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def fine_report():
    return controller.fine_report()


@admin_bp.route("/reports/vehicles", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def vehicle_report():
    return controller.vehicle_report()


@admin_bp.route("/reports/disputes", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def dispute_report():
    return controller.dispute_report()


@admin_bp.route("/reports/notifications", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def notification_report():
    return controller.notification_report()


@admin_bp.route("/reports/system", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def full_system_report():
    return controller.full_system_report()

@admin_bp.route(
    "/reports/export",
    methods=["GET"]
)
@jwt_required()
@roles_required("ADMIN")
def export_report():

    return controller.export_report()