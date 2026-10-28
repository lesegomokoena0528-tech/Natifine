from flask import Blueprint

from app.controllers.citizen_controller import CitizenController

citizen_bp = Blueprint(

    "citizen",

    __name__,

    url_prefix="/api/citizen"

)

citizen_bp.get("/dashboard")(CitizenController.dashboard)