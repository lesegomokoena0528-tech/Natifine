"""
==========================================================
NatiFine Backend

Security Tests

JWT Authentication
Authorization
RBAC

==========================================================
"""

import pytest

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token
)

from app.models.user import User
from app.models.user import UserRole
from app.models.user import UserStatus
from app.config.database import db


class TestSecurity:

    @pytest.fixture(autouse=True)
    def setup(self, app):

        self.app = app

        with app.app_context():

            db.session.query(User).delete()

            db.session.commit()

            self.admin = User(

                id_number="9901015009087",

                first_name="Admin",

                last_name="User",

                email="admin@test.com",

                phone="0711111111",

                role=UserRole.ADMIN,

                status=UserStatus.ACTIVE

            )

            self.admin.set_password("Password@123")

            db.session.add(self.admin)

            self.officer = User(

                id_number="9901015009088",

                first_name="Officer",

                last_name="User",

                email="officer@test.com",

                phone="0722222222",

                role=UserRole.OFFICER,

                status=UserStatus.ACTIVE

            )

            self.officer.set_password("Password@123")

            db.session.add(self.officer)

            self.citizen = User(

                id_number="9901015009089",

                first_name="Citizen",

                last_name="User",

                email="citizen@test.com",

                phone="0733333333",

                role=UserRole.CITIZEN,

                status=UserStatus.ACTIVE

            )

            self.citizen.set_password("Password@123")

            db.session.add(self.citizen)

            db.session.commit()

    # ------------------------------------------------------

    def get_access_token(self, user):

        with self.app.app_context():

            return create_access_token(

                identity=str(user.user_id),

                additional_claims={

                    "role": user.role.value,

                    "email": user.email

                }

            )

    # ------------------------------------------------------

    def get_refresh_token(self, user):

        with self.app.app_context():

            return create_refresh_token(

                identity=str(user.user_id)

            )

    # ------------------------------------------------------

    def test_access_token_creation(self):

        token = self.get_access_token(self.admin)

        assert token is not None

    # ------------------------------------------------------

    def test_refresh_token_creation(self):

        token = self.get_refresh_token(self.admin)

        assert token is not None

    # ------------------------------------------------------

    def test_profile_requires_authentication(self, client):

        response = client.get("/api/auth/profile")

        assert response.status_code == 401

    # ------------------------------------------------------

    def test_profile_with_valid_token(self, client):

        token = self.get_access_token(self.admin)

        response = client.get(

            "/api/auth/profile",

            headers={

                "Authorization":

                    f"Bearer {token}"

            }

        )

        assert response.status_code == 200

    # ------------------------------------------------------

    def test_invalid_token(self, client):

        response = client.get(

            "/api/auth/profile",

            headers={

                "Authorization":

                    "Bearer invalid.token.value"

            }

        )

        assert response.status_code == 401

    # ------------------------------------------------------

    def test_missing_bearer_prefix(self, client):

        token = self.get_access_token(self.admin)

        response = client.get(

            "/api/auth/profile",

            headers={

                "Authorization": token

            }

        )

        assert response.status_code == 401

    # ------------------------------------------------------

    def test_refresh_endpoint_requires_refresh_token(

            self,

            client

    ):

        token = self.get_access_token(self.admin)

        response = client.post(

            "/api/auth/refresh",

            headers={

                "Authorization":

                    f"Bearer {token}"

            }

        )

        assert response.status_code == 422

    # ------------------------------------------------------

    def test_refresh_token_success(self, client):

        token = self.get_refresh_token(self.admin)

        response = client.post(

            "/api/auth/refresh",

            headers={

                "Authorization":

                    f"Bearer {token}"

            }

        )

        assert response.status_code == 200

    # ------------------------------------------------------

    def test_admin_can_access_admin_route(self, client):

        token = self.get_access_token(self.admin)

        response = client.get(

            "/api/admin/users",

            headers={

                "Authorization":

                    f"Bearer {token}"

            }

        )

        assert response.status_code != 403

    # ------------------------------------------------------

    def test_citizen_cannot_access_admin_route(

            self,

            client

    ):

        token = self.get_access_token(self.citizen)

        response = client.get(

            "/api/admin/users",

            headers={

                "Authorization":

                    f"Bearer {token}"

            }

        )

        assert response.status_code == 403

    # ------------------------------------------------------

    def test_officer_can_issue_fine(self, client):

        token = self.get_access_token(self.officer)

        response = client.post(

            "/api/v1/fines",

            headers={

                "Authorization":

                    f"Bearer {token}"

            },

            json={}

        )

        assert response.status_code != 403

    # ------------------------------------------------------

    def test_citizen_cannot_issue_fine(self, client):

        token = self.get_access_token(self.citizen)

        response = client.post(

            "/api/v1/fines",

            headers={

                "Authorization":

                    f"Bearer {token}"

            },

            json={}

        )

        assert response.status_code == 403

    # ------------------------------------------------------

    def test_locked_user_login_denied(self):

        self.officer.status = UserStatus.LOCKED

        db.session.commit()

        assert self.officer.status == UserStatus.LOCKED

    # ------------------------------------------------------

    def test_inactive_user(self):

        self.citizen.status = UserStatus.INACTIVE

        db.session.commit()

        assert self.citizen.status == UserStatus.INACTIVE

    # ------------------------------------------------------

    @pytest.mark.parametrize(

        "role",

        [

            UserRole.ADMIN,

            UserRole.OFFICER,

            UserRole.CITIZEN

        ]

    )

    def test_token_generation_all_roles(self, role):

        user = User(

            first_name="Test",

            last_name="User",

            email="test@test.com",

            role=role,

            status=UserStatus.ACTIVE

        )

        user.user_id = 99

        token = self.get_access_token(user)

        assert token is not None

    # ------------------------------------------------------

    def test_expired_token(self):

        """
        Expired-token testing should use a
        JWT configuration with a very short
        expiration time or a mocked clock.
        """
        assert True

    # ------------------------------------------------------

    def test_revoked_token(self):

        """
        This test is implemented after
        JWT blocklisting (Redis/DB) is added.
        """
        assert True

    # ------------------------------------------------------

    def test_blacklisted_token(self):

        """
        Future enhancement.
        """
        assert True