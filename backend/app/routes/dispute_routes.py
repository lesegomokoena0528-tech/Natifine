from flask import Blueprint

from app.controllers.dispute_controller import DisputeController

from app.middleware.auth import login_required
from app.middleware.roles import roles_required

from app.constants.roles import Roles


dispute_bp = Blueprint(
    "disputes",
    __name__,
    url_prefix="/api/v1/disputes"
)

# ==========================================================
# SUBMIT DISPUTE
# ==========================================================

@dispute_bp.post("")
@login_required
@roles_required(Roles.CITIZEN.value)
def submit_dispute():
    return DisputeController.submit()


# ==========================================================
# MY DISPUTES
# ==========================================================

@dispute_bp.get("")
@login_required
@roles_required(Roles.CITIZEN.value)
def my_disputes():
    return DisputeController.my_disputes()


# ==========================================================
# DISPUTE DETAILS
# ==========================================================

@dispute_bp.get("/<int:dispute_id>")
@login_required
@roles_required(
    Roles.CITIZEN.value,
    Roles.OFFICER.value,
    Roles.ADMIN.value
)
def dispute_details(dispute_id):
    return DisputeController.details(dispute_id)


# ==========================================================
# UPLOAD SUPPORTING DOCUMENT
# ==========================================================

@dispute_bp.post("/<int:dispute_id>/documents")
@login_required
@roles_required(Roles.CITIZEN.value)
def upload_document(dispute_id):
    return DisputeController.upload_document(dispute_id)


# ==========================================================
# PENDING REVIEWS
# ==========================================================

@dispute_bp.get("/pending")
@login_required
@roles_required(
    Roles.OFFICER.value,
    Roles.ADMIN.value
)
def pending_reviews():
    return DisputeController.pending()


# ==========================================================
# APPROVE DISPUTE
# ==========================================================

@dispute_bp.patch("/<int:dispute_id>/approve")
@login_required
@roles_required(
    Roles.OFFICER.value,
    Roles.ADMIN.value
)
def approve_dispute(dispute_id):
    return DisputeController.approve(dispute_id)


# ==========================================================
# REJECT DISPUTE
# ==========================================================

@dispute_bp.patch("/<int:dispute_id>/reject")
@login_required
@roles_required(
    Roles.OFFICER.value,
    Roles.ADMIN.value
)
def reject_dispute(dispute_id):
    return DisputeController.reject(dispute_id)


# ==========================================================
# REQUEST MORE INFORMATION
# ==========================================================

@dispute_bp.patch("/<int:dispute_id>/request-information")
@login_required
@roles_required(
    Roles.OFFICER.value,
    Roles.ADMIN.value
)
def request_information(dispute_id):
    return DisputeController.request_information(dispute_id)


# ==========================================================
# SEARCH
# ==========================================================

@dispute_bp.get("/search")
@login_required
@roles_required(
    Roles.OFFICER.value,
    Roles.ADMIN.value
)
def search_disputes():
    return DisputeController.search()


# ==========================================================
# STATISTICS
# ==========================================================

@dispute_bp.get("/statistics")
@login_required
@roles_required(Roles.ADMIN.value)
def statistics():
    return DisputeController.statistics()