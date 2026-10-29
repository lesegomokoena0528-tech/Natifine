import os
from sqlalchemy.engine import URL


def _bool_env(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def _is_vercel_environment():
    return _bool_env("VERCEL") or bool(os.getenv("VERCEL_ENV"))


def _database_url_from_env():
    """Return the first configured managed-database URL.

    Vercel + Neon (and most Postgres integrations) expose several names.
    ``DATABASE_URL`` stays first for backwards compatibility, then the
    Vercel/Neon variables. Blank values are ignored.
    """
    for name in (
        "DATABASE_URL",
        "POSTGRES_URL",
        "POSTGRES_URL_NON_POOLING",
        "DATABASE_URL_UNPOOLED",
    ):
        value = os.getenv(name)
        if value and value.strip():
            value = value.strip().strip('"').strip("'")
            break
    else:
        value = None

    if value:
        normalized = _normalize_database_url(value)
        if not normalized.startswith(
            ("mysql+pymysql://", "postgresql+psycopg2://")
        ):
            raise RuntimeError(
                "The configured database URL is invalid. Provide a complete "
                "MySQL or PostgreSQL connection URL, not a password alone."
            )

    if _is_vercel_environment():
        if not value:
            raise RuntimeError(
                "Vercel requires DATABASE_URL or POSTGRES_URL for the "
                "persistent Postgres database."
            )

        normalized = _normalize_database_url(value)
        if not normalized.startswith("postgresql+psycopg2://"):
            raise RuntimeError(
                "Vercel requires a Postgres URL in DATABASE_URL or "
                "POSTGRES_URL; local MySQL settings are not persistent."
            )

    return value


def _normalize_database_url(uri):
    """Allow generic database URLs from hosting providers."""
    if not uri:
        return uri
    # SQLAlchemy needs an explicit driver for MySQL and Postgres.
    if uri.startswith("mysql://"):
        uri = uri.replace("mysql://", "mysql+pymysql://", 1)
    elif uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg2://", 1)
    elif uri.startswith("postgresql://"):
        uri = uri.replace("postgresql://", "postgresql+psycopg2://", 1)
    return uri


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # ------------------------------------------------------
    # Database
    # ------------------------------------------------------
    # Prefer an explicit managed URL (Vercel Postgres/Neon, Render, managed MySQL).
    # Fall back to discrete DB_* variables for local development.
    _database_url = _normalize_database_url(_database_url_from_env())

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

    # Recycle connections before the database's idle timeout and verify
    # liveness. Serverless functions are short-lived, so keep the pool small
    # and let the provider-side pooler (Neon pgbouncer) do the heavy lifting.
    _database_uri_string = str(SQLALCHEMY_DATABASE_URI or "")
    _engine_options = {}

    if _database_uri_string.startswith(("mysql", "postgresql")):
        _engine_options["pool_pre_ping"] = True
        _engine_options["pool_recycle"] = int(
            os.getenv("DB_POOL_RECYCLE", "280")
        )

    if _database_uri_string.startswith("postgresql"):
        _engine_options.update({
            "pool_size": int(os.getenv("DB_POOL_SIZE", "2")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "3")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "10")),
        })

    if _bool_env("DB_SSL") and _database_uri_string.startswith("mysql"):
        # Managed MySQL (Aiven, PlanetScale-style) requires TLS.
        _engine_options["connect_args"] = {"ssl": {}}

    SQLALCHEMY_ENGINE_OPTIONS = _engine_options

    # ------------------------------------------------------
    # CORS
    # ------------------------------------------------------
    # Comma-separated list of allowed browser origins.
    # Example: https://natifine.vercel.app,http://localhost:5000
    _cors = os.getenv("CORS_ORIGINS", "")
    CORS_ORIGINS = [o.strip() for o in _cors.split(",") if o.strip()]

    # ------------------------------------------------------
    # Uploads / Blob storage
    # ------------------------------------------------------
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    # auto = use Vercel Blob when credentials are present, otherwise local disk.
    # Force with "local" or "vercel_blob".
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "auto")
    BLOB_READ_WRITE_TOKEN = (
        os.getenv("BLOB_READ_WRITE_TOKEN")
        or os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")
    )
    BLOB_STORE_ID = os.getenv("BLOB_STORE_ID")
    BLOB_ACCESS = os.getenv("BLOB_ACCESS", "private")

    # Vercel Functions limit request bodies to 4.5 MB. Keep the default below
    # that limit; override locally if larger uploads are needed.
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", str(4 * 1024 * 1024))
    )

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
