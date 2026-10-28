from flask import Blueprint

from app.controllers.auth_controller import AuthController

auth_bp = Blueprint(

    "auth",

    __name__,

    url_prefix="/api/auth"

)

auth_bp.post("/register")(AuthController.register)

auth_bp.post("/login")(AuthController.login)

auth_bp.post("/refresh")(AuthController.refresh)

auth_bp.get("/profile")(AuthController.profile)

auth_bp.put("/change-password")(AuthController.change_password)