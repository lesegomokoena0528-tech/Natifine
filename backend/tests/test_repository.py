"""
==========================================================
NatiFine Backend

Repository Layer Tests

Author : NatiFine Development Team
==========================================================
"""

import pytest

from app.config.database import db
from app.models.user import User
from app.models.user import UserRole
from app.models.user import UserStatus
from app.repositories.user_repository import UserRepository


class TestUserRepository:

    @pytest.fixture(autouse=True)
    def setup(self, app):

        self.repository = UserRepository()

        with app.app_context():

            db.session.query(User).delete()

            db.session.commit()

            user1 = User(

                id_number="9901015009087",

                first_name="John",

                last_name="Smith",

                email="john@test.com",

                phone="0711111111",

                role=UserRole.ADMIN,

                status=UserStatus.ACTIVE

            )

            user1.set_password("Password@123")

            user2 = User(

                id_number="0001015009087",

                first_name="Jane",

                last_name="Brown",

                email="jane@test.com",

                phone="0722222222",

                role=UserRole.CITIZEN,

                status=UserStatus.ACTIVE

            )

            user2.set_password("Password@123")

            user3 = User(

                id_number="0101015009087",

                first_name="Mike",

                last_name="Jones",

                email="mike@test.com",

                phone="0733333333",

                role=UserRole.OFFICER,

                status=UserStatus.LOCKED

            )

            user3.set_password("Password@123")

            db.session.add_all([user1, user2, user3])

            db.session.commit()

    # --------------------------------------------------

    def test_find_all(self, app):

        with app.app_context():

            users = self.repository.find_all()

            assert len(users) == 3

    # --------------------------------------------------

    def test_count(self, app):

        with app.app_context():

            assert self.repository.count() == 3

    # --------------------------------------------------

    def test_find_by_email(self, app):

        with app.app_context():

            user = self.repository.find_by_email(

                "john@test.com"

            )

            assert user is not None

            assert user.first_name == "John"

    # --------------------------------------------------

    def test_find_by_phone(self, app):

        with app.app_context():

            user = self.repository.find_by_phone(

                "0711111111"

            )

            assert user.email == "john@test.com"

    # --------------------------------------------------

    def test_find_by_id_number(self, app):

        with app.app_context():

            user = self.repository.find_by_id_number(

                "9901015009087"

            )

            assert user.first_name == "John"

    # --------------------------------------------------

    def test_find_by_role(self, app):

        with app.app_context():

            admins = self.repository.find_by_role(

                UserRole.ADMIN

            )

            assert len(admins) == 1

            assert admins[0].email == "john@test.com"

    # --------------------------------------------------

    def test_find_by_status(self, app):

        with app.app_context():

            users = self.repository.find_by_status(

                UserStatus.ACTIVE

            )

            assert len(users) == 2

    # --------------------------------------------------

    def test_exists_by_email(self, app):

        with app.app_context():

            assert self.repository.exists_by_email(

                "john@test.com"

            ) is True

            assert self.repository.exists_by_email(

                "none@test.com"

            ) is False

    # --------------------------------------------------

    def test_exists_by_phone(self, app):

        with app.app_context():

            assert self.repository.exists_by_phone(

                "0711111111"

            )

            assert not self.repository.exists_by_phone(

                "0799999999"

            )

    # --------------------------------------------------

    def test_exists_by_id_number(self, app):

        with app.app_context():

            assert self.repository.exists_by_id_number(

                "9901015009087"

            )

            assert not self.repository.exists_by_id_number(

                "123"

            )

    # --------------------------------------------------

    def test_find_login_user_email(self, app):

        with app.app_context():

            user = self.repository.find_login_user(

                "john@test.com"

            )

            assert user.email == "john@test.com"

    # --------------------------------------------------

    def test_find_login_user_phone(self, app):

        with app.app_context():

            user = self.repository.find_login_user(

                "0711111111"

            )

            assert user.first_name == "John"

    # --------------------------------------------------

    def test_find_login_user_id_number(self, app):

        with app.app_context():

            user = self.repository.find_login_user(

                "9901015009087"

            )

            assert user.last_name == "Smith"

    # --------------------------------------------------

    def test_search_first_name(self, app):

        with app.app_context():

            users = self.repository.search("John")

            assert len(users) == 1

    # --------------------------------------------------

    def test_search_last_name(self, app):

        with app.app_context():

            users = self.repository.search("Brown")

            assert len(users) == 1

    # --------------------------------------------------

    def test_search_email(self, app):

        with app.app_context():

            users = self.repository.search("mike")

            assert len(users) == 1

    # --------------------------------------------------

    def test_search_empty(self, app):

        with app.app_context():

            users = self.repository.search("XYZ")

            assert len(users) == 0

    # --------------------------------------------------

    def test_save(self, app):

        with app.app_context():

            user = User(

                id_number="0202025009087",

                first_name="Peter",

                last_name="White",

                email="peter@test.com",

                phone="0744444444",

                role=UserRole.CITIZEN,

                status=UserStatus.ACTIVE

            )

            user.set_password("Password@123")

            saved = self.repository.save(user)

            assert saved.user_id is not None

    # --------------------------------------------------

    def test_update(self, app):

        with app.app_context():

            user = self.repository.find_by_email(

                "john@test.com"

            )

            user.first_name = "Johnny"

            self.repository.update()

            updated = self.repository.find_by_email(

                "john@test.com"

            )

            assert updated.first_name == "Johnny"

    # --------------------------------------------------

    def test_delete(self, app):

        with app.app_context():

            user = self.repository.find_by_email(

                "john@test.com"

            )

            self.repository.delete(user)

            assert self.repository.count() == 2

    # --------------------------------------------------

    def test_find_by_id(self, app):

        with app.app_context():

            user = self.repository.find_by_email(

                "john@test.com"

            )

            found = self.repository.find_by_id(

                user.user_id

            )

            assert found.email == "john@test.com"

    # --------------------------------------------------

    def test_exists(self, app):

        with app.app_context():

            user = self.repository.find_by_email(

                "john@test.com"

            )

            assert self.repository.exists(

                user.user_id

            )

    # --------------------------------------------------

    def test_pagination(self, app):

        with app.app_context():

            page = self.repository.paginate(

                page=1,

                size=2

            )

            assert len(page.items) == 2

            assert page.total == 3

    # --------------------------------------------------

    def test_admins(self, app):

        with app.app_context():

            admins = self.repository.admins()

            assert len(admins) == 1

    # --------------------------------------------------

    def test_officers(self, app):

        with app.app_context():

            officers = self.repository.officers()

            assert len(officers) == 1

    # --------------------------------------------------

    def test_citizens(self, app):

        with app.app_context():

            citizens = self.repository.citizens()

            assert len(citizens) == 1

    # --------------------------------------------------

    def test_active_users(self, app):

        with app.app_context():

            users = self.repository.active_users()

            assert len(users) == 2

    # --------------------------------------------------

    def test_non_existing_email(self, app):

        with app.app_context():

            user = self.repository.find_by_email(

                "unknown@test.com"

            )

            assert user is None

    # --------------------------------------------------

    def test_non_existing_phone(self, app):

        with app.app_context():

            user = self.repository.find_by_phone(

                "0700000000"

            )

            assert user is None

    # --------------------------------------------------

    def test_non_existing_id_number(self, app):

        with app.app_context():

            user = self.repository.find_by_id_number(

                "1111111111111"

            )

            assert user is None