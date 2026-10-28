import os
from sqlalchemy.engine import URL


def _bool_env(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def _normalize_database_url(uri):
    """Allow generic MySQL URLs from hosting providers."""
    if not uri:
        return uri
    # SQLAlchemy needs an explicit driver for MySQL.
    if uri.startswith("mysql://"):
        uri = uri.replace("mysql://", "mysql+pymysql://", 1)
    return uri


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # ------------------------------------------------------
    # Database
    # ------------------------------------------------------
    # Prefer an explicit DATABASE_URL (Render, managed MySQL).
    # Fall back to discrete DB_* variables for local development.
    _database_url = _normalize_database_url(os.getenv("DATABASE_URL"))

    if _database_url:
        SQLALCHEMY_DATABASE_URI = _database_url
    else:
        _db_user = os.getenv("DB_USER", "root")
        _db_password = os.getenv("DB_PASSWORD", "")
        _db_host = os.getenv("DB_HOST", "localhost")
        _db_port = int(os.getenv("DB_PORT", "3306"))
        _db_name = os.getenv("DB_NAME", "natifine")

        SQLALCHEMY_DATABASE_URI = URL.create(
            drivername="mysql+pymysql",
            username=_db_user,
            password=_db_password,
            host=_db_host,
            port=_db_port,
            database=_db_name
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Recycle connections before MySQL's idle timeout and verify liveness.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "280")),
    }

    if _bool_env("DB_SSL"):
        # Managed MySQL (Aiven, PlanetScale-style) requires TLS.
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {"ssl": {}}

    # ------------------------------------------------------
    # CORS
    # ------------------------------------------------------
    # Comma-separated list of allowed browser origins.
    # Example: https://natifine.vercel.app,http://localhost:5000
    _cors = os.getenv("CORS_ORIGINS", "")
    CORS_ORIGINS = [o.strip() for o in _cors.split(",") if o.strip()]

    # ------------------------------------------------------
    # Uploads
    # ------------------------------------------------------
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # ------------------------------------------------------
    # Email (SMTP)
    # ------------------------------------------------------
    # Accepts either MAIL_* or SMTP_* variable names so the same
    # configuration works with common provider setup guides.
    _mail_server = os.getenv("MAIL_SERVER") or os.getenv("SMTP_SERVER", "localhost")
    _mail_port = int(os.getenv("MAIL_PORT") or os.getenv("SMTP_PORT", "25"))
    _mail_username = os.getenv("MAIL_USERNAME") or os.getenv("SMTP_USERNAME")
    _mail_password = os.getenv("MAIL_PASSWORD") or os.getenv("SMTP_PASSWORD")

    MAIL_SERVER = _mail_server
    MAIL_PORT = _mail_port
    MAIL_USE_TLS = _bool_env(
        "MAIL_USE_TLS", "true" if _mail_port == 587 else "false"
    )
    MAIL_USE_SSL = _bool_env(
        "MAIL_USE_SSL", "true" if _mail_port == 465 else "false"
    )
    MAIL_USERNAME = _mail_username
    MAIL_PASSWORD = _mail_password
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_DEFAULT_SENDER")
        or _mail_username
        or "no-reply@natifine.gov.za"
    )
    MAIL_SUPPRESS_SEND = _bool_env("MAIL_SUPPRESS_SEND", "false")
