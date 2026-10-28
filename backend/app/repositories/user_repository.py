from sqlalchemy import or_

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):

    def __init__(self):
        super().__init__(User)

    # ------------------------
    # EMAIL
    # ------------------------

    def find_by_email(self, email):

        return User.query.filter_by(
            email=email
        ).first()

    # ------------------------
    # ID NUMBER
    # ------------------------

    def find_by_id_number(self, id_number):

        return User.query.filter_by(
            id_number=id_number
        ).first()

    # ------------------------
    # PHONE
    # ------------------------

    def find_by_phone(self, phone):

        return User.query.filter_by(
            phone=phone
        ).first()

    # ------------------------
    # ROLE
    # ------------------------

    def find_by_role(self, role):

        return User.query.filter_by(
            role=role
        ).all()

    # ------------------------
    # STATUS
    # ------------------------

    def find_by_status(self, status):

        return User.query.filter_by(
            status=status
        ).all()

    # ------------------------
    # SEARCH
    # ------------------------

    def search(self, keyword):

        return User.query.filter(

            or_(

                User.first_name.ilike(f"%{keyword}%"),

                User.last_name.ilike(f"%{keyword}%"),

                User.email.ilike(f"%{keyword}%"),

                User.id_number.ilike(f"%{keyword}%")
            )

        ).all()

    # ------------------------
    # DUPLICATE CHECK
    # ------------------------

    def exists_by_email(self, email):

        return self.find_by_email(email) is not None

    def exists_by_phone(self, phone):

        return self.find_by_phone(phone) is not None

    def exists_by_id_number(self, id_number):

        return self.find_by_id_number(id_number) is not None

    # ------------------------
    # LOGIN
    # ------------------------

    def find_login_user(self, username):

        return User.query.filter(

            or_(

                User.email == username,

                User.phone == username,

                User.id_number == username

            )

        ).first()

    # ------------------------
    # ACTIVE USERS
    # ------------------------

    def active_users(self):

        return User.query.filter_by(
            status="ACTIVE"
        ).all()

    # ------------------------
    # OFFICERS
    # ------------------------

    def officers(self):

        return User.query.filter_by(
            role="OFFICER"
        ).all()

    # ------------------------
    # ADMINS
    # ------------------------

    def admins(self):

        return User.query.filter_by(
            role="ADMIN"
        ).all()

    # ------------------------
    # CITIZENS
    # ------------------------

    def citizens(self):

        return User.query.filter_by(
            role="CITIZEN"
        ).all()