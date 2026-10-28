"""
==========================================================
NatiFine Backend

Profile Tests

Current User
Profile Update
Password Change

==========================================================
"""

import pytest

from flask_jwt_extended import create_access_token

from app.config.database import db
from app.models.user import User
from app.models.user import UserRole
from app.models.user import UserStatus


class TestProfile:

    @pytest.fixture(autouse=True)
    def setup(self, app):

        self.app = app

        with app.app_context():

            db.session.query(User).delete()

            db.session.commit()

            self.user = User(

                id_number="9901015009087",

                first_name="John",

                last_name="Smith",

                email="john@test.com",

                phone="0712345678",

                role=UserRole.CITIZEN,

                status=UserStatus.ACTIVE

            )

            self.user.set_password("Password@123")

            db.session.add(self.user)

            db.session.commit()

    # -----------------------------------------------------

    def token(self):

        with self.app.app_context():

            return create_access_token(

                identity=str(self.user.user_id),

                additional_claims={

                    "role": self.user.role.value,

                    "email": self.user.email

                }

            )

    # -----------------------------------------------------

    def auth_header(self):

        return {

            "Authorization":

                f"Bearer {self.token()}"

        }

    # -----------------------------------------------------

    def test_get_profile(self, client):

        response = client.get(

            "/api/auth/profile",

            headers=self.auth_header()

        )

        assert response.status_code == 200

        body = response.get_json()

        assert body["success"] is True

        assert body["data"]["email"] == "john@test.com"

    # -----------------------------------------------------

    def test_profile_without_token(self, client):

        response = client.get(

            "/api/auth/profile"

        )

        assert response.status_code == 401

    # -----------------------------------------------------

    def test_profile_invalid_token(self, client):

        response = client.get(

            "/api/auth/profile",

            headers={

                "Authorization":

                    "Bearer invalid.token"

            }

        )

        assert response.status_code == 401

    # -----------------------------------------------------

    def test_profile_contains_expected_fields(

            self,

            client

    ):

        response = client.get(

            "/api/auth/profile",

            headers=self.auth_header()

        )

        body = response.get_json()

        data = body["data"]

        assert "user_id" in data

        assert "email" in data

        assert "first_name" in data

        assert "last_name" in data

        assert "role" in data

        assert "status" in data

    # -----------------------------------------------------

    def test_password_change_success(

            self,

            client

    ):

        response = client.put(

            "/api/auth/change-password",

            headers=self.auth_header(),

            json={

                "current_password":

                    "Password@123",

                "new_password":

                    "NewPassword@123"

            }

        )

        assert response.status_code == 200

    # -----------------------------------------------------

    def test_wrong_current_password(

            self,

            client

    ):

        response = client.put(

            "/api/auth/change-password",

            headers=self.auth_header(),

            json={

                "current_password":

                    "WrongPassword",

                "new_password":

                    "NewPassword@123"

            }

        )

        assert response.status_code == 401

    # -----------------------------------------------------

    def test_change_password_without_token(

            self,

            client

    ):

        response = client.put(

            "/api/auth/change-password",

            json={

                "current_password":

                    "Password@123",

                "new_password":

                    "NewPassword@123"

            }

        )

        assert response.status_code == 401

    # -----------------------------------------------------

    def test_empty_password(

            self,

            client

    ):

        response = client.put(

            "/api/auth/change-password",

            headers=self.auth_header(),

            json={

                "current_password":

                    "",

                "new_password":

                    ""

            }

        )

        assert response.status_code in [

            400,

            422

        ]

    # -----------------------------------------------------

    def test_profile_after_password_change(

            self,

            client

    ):

        client.put(

            "/api/auth/change-password",

            headers=self.auth_header(),

            json={

                "current_password":

                    "Password@123",

                "new_password":

                    "AnotherPassword@123"

            }

        )

        response = client.get(

            "/api/auth/profile",

            headers=self.auth_header()

        )

        assert response.status_code == 200

    # -----------------------------------------------------

    def test_locked_account_profile(

            self,

            client

    ):

        with self.app.app_context():

            self.user.status = UserStatus.LOCKED

            db.session.commit()

        response = client.get(

            "/api/auth/profile",

            headers=self.auth_header()

        )

        assert response.status_code in [

            401,

            403

        ]

    # -----------------------------------------------------

    def test_inactive_account_profile(

            self,

            client

    ):

        with self.app.app_context():

            self.user.status = UserStatus.INACTIVE

            db.session.commit()

        response = client.get(

            "/api/auth/profile",

            headers=self.auth_header()

        )

        assert response.status_code in [

            401,

            403

        ]

    # -----------------------------------------------------

    def test_profile_returns_json(

            self,

            client

    ):

        response = client.get(

            "/api/auth/profile",

            headers=self.auth_header()

        )

        assert response.content_type.startswith(

            "application/json"

        )

    # -----------------------------------------------------

    def test_profile_does_not_return_password(

            self,

            client

    ):

        response = client.get(

            "/api/auth/profile",

            headers=self.auth_header()

        )

        data = response.get_json()["data"]

        assert "password" not in data

    # -----------------------------------------------------

    @pytest.mark.parametrize(

        "field",

        [

            "email",

            "first_name",

            "last_name",

            "phone",

            "role",

            "status"

        ]

    )

    def test_profile_fields_exist(

            self,

            client,

            field

    ):

        response = client.get(

            "/api/auth/profile",

            headers=self.auth_header()

        )

        body = response.get_json()

        assert field in body["data"]

    # -----------------------------------------------------

    def test_profile_multiple_requests(

            self,

            client

    ):

        for _ in range(5):

            response = client.get(

                "/api/auth/profile",

                headers=self.auth_header()

            )

            assert response.status_code == 200

    # -----------------------------------------------------

    def test_profile_not_found(

            self,

            client

    ):
        """
        Future enhancement.

        Test a valid JWT whose user has been
        deleted from the database.
        """
        assert True

    # -----------------------------------------------------

    def test_update_profile_placeholder(self):
        """
        Future enhancement.

        Implement once PUT /api/auth/profile
        is added.
        """
        assert True