from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy(
    session_options={
        "expire_on_commit": False,
        "autoflush": True,
        "autocommit": False
    }
)

migrate = Migrate()