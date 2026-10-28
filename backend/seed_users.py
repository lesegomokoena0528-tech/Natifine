from app.factory import create_app
from app.config.database import db
from app.models.user import User, UserRole, UserStatus

app = create_app()

with app.app_context():

    # ------------------------
    # ADMIN
    # ------------------------
    if not User.query.filter_by(email="admin@natifine.gov.za").first():

        admin = User(
            id_number="8001015009087",
            first_name="System",
            last_name="Administrator",
            email="admin@natifine.gov.za",
            phone="0711111111",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )

        admin.set_password("Admin@123")

        db.session.add(admin)

    # ------------------------
    # OFFICER
    # ------------------------
    if not User.query.filter_by(email="mlambonyiko@natifine.gov.za").first():

        officer = User(
            id_number="8505055009086",
            first_name="Nyiko",
            last_name="Mlambo",
            email="mlambonyiko@natifine.gov.za",
            phone="0722222222",
            role=UserRole.OFFICER,
            status=UserStatus.ACTIVE
        )

        officer.set_password("Officer@123")

        db.session.add(officer)

    db.session.commit()

    print("✅ Admin and Officer created successfully.")