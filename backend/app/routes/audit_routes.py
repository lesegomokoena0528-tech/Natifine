from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.audit_controller import AuditController
from app.middleware.roles import roles_required

audit_bp = Blueprint(

    "audit",

    __name__,

    url_prefix="/api/admin/audit"

)

controller = AuditController()


@audit_bp.route("", methods=["GET"])
@jwt_required()
@roles_required("ADMIN")
def get_logs():
    return controller.get_logs()


@audit_bp.route("/user/<string:user_id>")
@jwt_required()
@roles_required("ADMIN")
def user_logs(user_id):
    return controller.user_logs(user_id)


@audit_bp.route("/action/<action>")
@jwt_required()
@roles_required("ADMIN")
def action_logs(action):
    return controller.action_logs(action)


@audit_bp.route("/entity/<entity>")
@jwt_required()
@roles_required("ADMIN")
def entity_logs(entity):
    return controller.entity_logs(entity)