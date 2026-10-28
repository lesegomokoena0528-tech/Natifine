from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.notification_controller import NotificationController
from app.middleware.roles import roles_required

notification_bp = Blueprint(
    "notifications",
    __name__,
    url_prefix="/api/notifications"
)

controller = NotificationController()

# ==========================================================
# SEND NOTIFICATION
# ==========================================================

@notification_bp.route(
    "/send",
    methods=["POST"]
)
@jwt_required()
@roles_required("ADMIN", "SYSTEM")
def send_notification():

    return controller.send_notification()


# ==========================================================
# SEND TEMPLATE
# ==========================================================

@notification_bp.route(
    "/template",
    methods=["POST"]
)
@jwt_required()
@roles_required("ADMIN", "SYSTEM")
def send_template():

    return controller.send_template()


# ==========================================================
# CURRENT USER NOTIFICATIONS
# ==========================================================

@notification_bp.route(
    "/me",
    methods=["GET"]
)
@jwt_required()
def my_notifications():

    return controller.my_notifications()


# ==========================================================
# LIST TEMPLATES
# ==========================================================

@notification_bp.route(
    "/templates",
    methods=["GET"]
)
@jwt_required()
@roles_required("ADMIN", "SYSTEM")
def templates():

    return controller.templates()


# ==========================================================
# GET NOTIFICATION
# ==========================================================

@notification_bp.route(
    "/<int:notification_id>",
    methods=["GET"]
)
@jwt_required()
@roles_required("ADMIN")
def get_notification(notification_id):

    return controller.get_notification(notification_id)


# ==========================================================
# MARK AS READ
# ==========================================================

@notification_bp.route(
    "/<int:notification_id>/read",
    methods=["PUT"]
)
@jwt_required()
def mark_read(notification_id):

    return controller.mark_read(notification_id)


# ==========================================================
# MARK AS DELIVERED
# ==========================================================

@notification_bp.route(
    "/<int:notification_id>/delivered",
    methods=["PUT"]
)
@jwt_required()
@roles_required("SYSTEM", "ADMIN")
def mark_delivered(notification_id):

    return controller.mark_delivered(notification_id)


# ==========================================================
# RETRY FAILED
# ==========================================================

@notification_bp.route(
    "/retry",
    methods=["POST"]
)
@jwt_required()
@roles_required("ADMIN")
def retry_failed():

    return controller.retry_failed()


# ==========================================================
# DASHBOARD STATISTICS
# ==========================================================

@notification_bp.route(
    "/statistics",
    methods=["GET"]
)
@jwt_required()
@roles_required("ADMIN")
def statistics():

    return controller.statistics()


# ==========================================================
# DELETE NOTIFICATION
# ==========================================================

@notification_bp.route(
    "/<int:notification_id>",
    methods=["DELETE"]
)
@jwt_required()
@roles_required("ADMIN")
def delete_notification(notification_id):

    return controller.delete_notification(notification_id)