import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.factory import create_app
from app.config.database import db
from app.config.settings import Config


def _base_database_url():
    """
    Return the configured database URL as a SQLAlchemy URL object.

    Config stores either a plain string (DATABASE_URL from hosting) or a
    URL object (local DB_* variables). Avoid str() on a URL object because
    SQLAlchemy masks the password when rendering it.
    """
    base = Config.SQLALCHEMY_DATABASE_URI
    if hasattr(base, "set"):
        return base
    return make_url(str(base))


def _test_database_url():
    """Derive a dedicated '<db>_test' schema so tests never touch dev data."""
    base = _base_database_url()
    return base.set(database=f"{base.database}_test")


class TestConfig(Config):
    """
    Isolated test configuration.

    The database URI must be supplied BEFORE create_app() runs because
    Flask-SQLAlchemy 3.x builds the engine during init_app(); overriding
    the config afterwards has no effect and would point tests at the real
    development database.

    Tests use a separate MySQL schema (same dialect as production) rather
    than in-memory SQLite, because the models rely on MySQL-side defaults
    (e.g. UUID() primary keys) that SQLite cannot reproduce.
    """

    TESTING = True

    SQLALCHEMY_DATABASE_URI = _test_database_url()

    SECRET_KEY = "testing-secret-key-32-bytes-minimum-000"

    JWT_SECRET_KEY = "testing-jwt-key-32-bytes-minimum-000000"

    MAIL_SUPPRESS_SEND = True


@pytest.fixture(scope="session", autouse=True)
def _ensure_test_database():
    """Create the '<db>_test' schema if it does not exist yet."""
    url = _test_database_url()
    admin_engine = create_engine(url.set(database=None))
    with admin_engine.begin() as conn:
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{url.database}` "
                "CHARACTER SET utf8mb4"
            )
        )
    admin_engine.dispose()
    yield


@pytest.fixture()
def app():

    app = create_app(TestConfig)

    with app.app_context():

        db.create_all()

        yield app

        db.session.remove()

        db.drop_all()


@pytest.fixture()
def client(app):

    return app.test_client()
