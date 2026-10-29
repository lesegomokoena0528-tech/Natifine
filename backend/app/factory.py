import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv

load_dotenv()

from app.config.settings import Config
from app.config.database import db, migrate
from app.config.mail import mail
from app.extensions import jwt, cors
from app.middleware.jwt_callbacks import configure_jwt
from docs.swagger import init_swagger

from app.routes.auth_routes import auth_bp
from app.routes.citizen_routes import citizen_bp
from app.routes.admin_routes import admin_bp
from app.routes.vehicle_routes import vehicle_bp
from app.routes.fine_routes import fine_bp
from app.routes.payment_routes import payment_bp
from app.routes.dispute_routes import dispute_bp
from app.routes.notification_routes import notification_bp
from app.routes.audit_routes import audit_bp


def create_app(config_class=None):
    # Serve the frontend from the project folder. Email templates are kept
    # inside the backend package so they are included in the Vercel function.
    frontend_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
    )
    template_folder_path = os.path.join(os.path.dirname(__file__), "templates")
    app = Flask(
        __name__,
        static_folder=frontend_folder_path,
        static_url_path="/static",
        template_folder=template_folder_path,
    )

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    configure_jwt(jwt)

    # CORS: restrict to configured browser origins. Falls back to "*"
    # only when CORS_ORIGINS is not set (e.g. local development).
    cors_origins = app.config.get("CORS_ORIGINS") or "*"
    cors.init_app(
        app,
        resources={r"/*": {"origins": cors_origins}},
        supports_credentials=False,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    mail.init_app(app)

    try:
        init_swagger(app)
    except Exception:
        pass

    # Register API blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(vehicle_bp)
    app.register_blueprint(fine_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(dispute_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(audit_bp)

    # Health check (Render). Must not expose sensitive data.
    @app.get("/healthz")
    def healthz():
        return {
            "status": "ok",
            "service": "natifine-api",
            "version": "1.0.0",
        }, 200

    # Frontend serving routes
    @app.route("/")
    def index():
        index_file = os.path.join(app.static_folder, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(app.static_folder, "index.html")
        return {
            "message": "NatiFine SA API is running. Access Swagger docs at /apidocs/",
            "version": "1.0.0"
        }

    @app.route("/<path:path>")
    def static_proxy(path):
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        # A missing concrete file (e.g. /pages/admin/vehicles.html) must not
        # silently fall back to the landing page. Only extensionless routes
        # (SPA-style) resolve to index.html.
        if os.path.splitext(path)[1]:
            return {"error": "Not Found", "message": f"Resource {path} not found."}, 404
        index_file = os.path.join(app.static_folder, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(app.static_folder, "index.html")
        return {"error": "Not Found", "message": f"Resource {path} not found."}, 404

    return app