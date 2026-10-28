from flask import Blueprint

from app.controllers.payment_controller import PaymentController

from app.middleware.auth import login_required
from app.middleware.roles import roles_required

from app.constants.roles import Roles

payment_bp = Blueprint(
    "payments",
    __name__,
    url_prefix="/api/v1/payments"
)

# ==========================================================
# CREATE PAYMENT
# ==========================================================

@payment_bp.post("")
@login_required
@roles_required(Roles.CITIZEN.value)
def create_payment():
    return PaymentController.create_payment()


# ==========================================================
# VERIFY PAYMENT
# ==========================================================

@payment_bp.post("/verify")
@login_required
@roles_required(
    Roles.CITIZEN.value,
    Roles.ADMIN.value,
    Roles.OFFICER.value
)
def verify_payment():
    return PaymentController.verify_payment()


# ==========================================================
# PAYMENT DETAILS
# ==========================================================

@payment_bp.get("/<int:payment_id>")
@login_required
@roles_required(
    Roles.CITIZEN.value,
    Roles.ADMIN.value,
    Roles.OFFICER.value
)
def payment_details(payment_id):
    return PaymentController.payment(payment_id)


# ==========================================================
# PAYMENT HISTORY
# ==========================================================

@payment_bp.get("/history")
@login_required
@roles_required(Roles.CITIZEN.value)
def payment_history():
    return PaymentController.history()


# ==========================================================
# DOWNLOAD RECEIPT
# ==========================================================

@payment_bp.get("/<int:payment_id>/receipt")
@login_required
@roles_required(
    Roles.CITIZEN.value,
    Roles.ADMIN.value
)
def download_receipt(payment_id):
    return PaymentController.receipt(payment_id)


# ==========================================================
# REQUEST REFUND
# ==========================================================

@payment_bp.post("/<int:payment_id>/refund")
@login_required
@roles_required(Roles.CITIZEN.value)
def request_refund(payment_id):
    return PaymentController.request_refund(payment_id)


# ==========================================================
# APPROVE REFUND
# ==========================================================

@payment_bp.patch("/refunds/<int:refund_id>/approve")
@login_required
@roles_required(Roles.ADMIN.value)
def approve_refund(refund_id):
    return PaymentController.approve_refund(refund_id)


# ==========================================================
# REJECT REFUND
# ==========================================================

@payment_bp.patch("/refunds/<int:refund_id>/reject")
@login_required
@roles_required(Roles.ADMIN.value)
def reject_refund(refund_id):
    return PaymentController.reject_refund(refund_id)


# ==========================================================
# LIST REFUNDS (citizen: own, admin: all)
# ==========================================================

@payment_bp.get("/refunds")
@login_required
@roles_required(
    Roles.CITIZEN.value,
    Roles.ADMIN.value
)
def list_refunds():
    return PaymentController.refunds()


# ==========================================================
# PAYMENT STATISTICS
# ==========================================================

@payment_bp.get("/statistics")
@login_required
@roles_required(Roles.ADMIN.value)
def payment_statistics():
    return PaymentController.statistics()


# ==========================================================
# SEARCH PAYMENTS
# ==========================================================

@payment_bp.get("/search")
@login_required
@roles_required(
    Roles.ADMIN.value,
    Roles.OFFICER.value
)
def search():
    return PaymentController.search()


# ==========================================================
# TOTALS
# ==========================================================

@payment_bp.get("/totals")
@login_required
@roles_required(Roles.CITIZEN.value)
def totals():
    return PaymentController.total_paid()


# ==========================================================
# PAYMENT GATEWAY WEBHOOK
# ==========================================================

@payment_bp.post("/webhook")
def payment_webhook():
    """
    Called by external payment gateways.

    No JWT authentication.

    Must verify gateway signature before processing.
    """
    return PaymentController.webhook()