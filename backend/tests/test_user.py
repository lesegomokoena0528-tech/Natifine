"""
==========================================================
NatiFine Backend

Unit Tests
User Model Tests

Author : NatiFine Development Team
==========================================================
"""

import pytest

from app.config.database import db
from app.models.user import User
from app.models.user import UserRole
from app.models.user import UserStatus


class TestUserModel:

    """
    Unit Tests for User Entity
    """

    def test_create_user(self, app):

        with app.app_context():

            user = User(

                id_number="9901015009087",

                first_name="John",

                last_name="Smith",

                email="john@test.com",

                phone="0712345678",

                role=UserRole.CITIZEN,

                status=UserStatus.ACTIVE

            )

            user.set_password("Password@123")

            db.session.add(user)

            db.session.commit()

            assert user.user_id is not None

            assert user.email == "john@test.com"

            assert user.role == UserRole.CITIZEN

            assert user.status == UserStatus.ACTIVE

    # ------------------------------------------------------

    def test_password_hashing(self, app):

        with app.app_context():

            user = User()

            user.set_password("Password@123")

            assert user.password != "Password@123"

            assert user.check_password("Password@123") is True

            assert user.check_password("WrongPassword") is False

    # ------------------------------------------------------

    def test_full_name_property(self):

        user = User(

            first_name="John",

            last_name="Smith"

        )

        assert user.full_name == "John Smith"

    # ------------------------------------------------------

    def test_admin_role(self):

        user = User(

            role=UserRole.ADMIN

        )

        assert user.is_admin() is True

        assert user.is_officer() is False

        assert user.is_citizen() is False

    # ------------------------------------------------------

    def test_officer_role(self):

        user = User(

            role=UserRole.OFFICER

        )

        assert user.is_officer() is True

        assert user.is_admin() is False

        assert user.is_citizen() is False

    # ------------------------------------------------------

    def test_citizen_role(self):

        user = User(

            role=UserRole.CITIZEN

        )

        assert user.is_citizen() is True

        assert user.is_admin() is False

        assert user.is_officer() is False

    # ------------------------------------------------------

    def test_active_status(self):

        user = User(

            status=UserStatus.ACTIVE

        )

        assert user.is_active() is True

    # ------------------------------------------------------

    def test_inactive_status(self):

        user = User(

            status=UserStatus.INACTIVE

        )

        assert user.is_active() is False

    # ------------------------------------------------------

    def test_locked_status(self):

        user = User(

            status=UserStatus.LOCKED

        )

        assert user.is_active() is False

    # ------------------------------------------------------

    def test_to_dict(self):

        user = User(

            user_id=1,

            id_number="9901015009087",

            first_name="John",

            last_name="Smith",

            email="john@test.com",

            phone="0712345678",

            role=UserRole.ADMIN,

            status=UserStatus.ACTIVE

        )

        result = user.to_dict()

        assert result["user_id"] == 1

        assert result["email"] == "john@test.com"

        assert result["role"] == "ADMIN"

        assert result["status"] == "ACTIVE"

        assert "password" not in result

    # ------------------------------------------------------

    @pytest.mark.parametrize(

        "role",

        [

            UserRole.ADMIN,

            UserRole.OFFICER,

            UserRole.CITIZEN

        ]

    )

    def test_roles(self, role):

        user = User(role=role)

        assert user.role == role

    # ------------------------------------------------------

    @pytest.mark.parametrize(

        "status",

        [

            UserStatus.ACTIVE,

            UserStatus.INACTIVE,

            UserStatus.LOCKED

        ]

    )

    def test_status_values(self, status):

        user = User(status=status)

        assert user.status == status

    # ------------------------------------------------------

    def test_email_uniqueness(self, app):

        with app.app_context():

            user1 = User(

                id_number="9901015009087",

                first_name="John",

                last_name="Smith",

                email="duplicate@test.com",

                phone="0712345678"

            )

            user1.set_password("Password@123")

            db.session.add(user1)

            db.session.commit()

            user2 = User(

                id_number="0001015009087",

                first_name="Jane",

                last_name="Smith",

                email="duplicate@test.com",

                phone="0712345679"

            )

            user2.set_password("Password@123")

            db.session.add(user2)

            with pytest.raises(Exception):

                db.session.commit()

            db.session.rollback()

    # ------------------------------------------------------

    def test_phone_uniqueness(self, app):

        with app.app_context():

            user1 = User(

                id_number="9901015009087",

                first_name="John",

                last_name="Smith",

                email="john@test.com",

                phone="0711111111"

            )

            user1.set_password("Password@123")

            db.session.add(user1)

            db.session.commit()

            user2 = User(

                id_number="0001015009087",

                first_name="Jane",

                last_name="Smith",

                email="jane@test.com",

                phone="0711111111"

            )

            user2.set_password("Password@123")

            db.session.add(user2)

            with pytest.raises(Exception):

                db.session.commit()

            db.session.rollback()

    # ------------------------------------------------------

    def test_id_number_uniqueness(self, app):

        with app.app_context():

            user1 = User(

                id_number="9901015009087",

                first_name="John",

                last_name="Smith",

                email="john@test.com",

                phone="0711111111"

            )

            user1.set_password("Password@123")

            db.session.add(user1)

            db.session.commit()

            user2 = User(

                id_number="9901015009087",

                first_name="Jane",

                last_name="Smith",

                email="jane@test.com",

                phone="0722222222"

            )

            user2.set_password("Password@123")

            db.session.add(user2)

            with pytest.raises(Exception):

                db.session.commit()

            db.session.rollback()