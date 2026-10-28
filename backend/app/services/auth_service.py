from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity
)

from app.models.user import (
    User,
    UserRole,
    UserStatus
)

from app.repositories.user_repository import UserRepository

from app.exceptions.auth_exceptions import *

from app.config.database import db


class AuthService:

    def __init__(self):

        self.repository = UserRepository()

    # ------------------------------------
    # REGISTER
    # ------------------------------------

    def register(self, data):

        if self.repository.exists_by_email(data["email"]):
            raise DuplicateUserException(
                "Email already exists."
            )

        if self.repository.exists_by_phone(data["phone"]):
            raise DuplicateUserException(
                "Phone number already exists."
            )

        if self.repository.exists_by_id_number(
                data["id_number"]):

            raise DuplicateUserException(
                "ID Number already exists."
            )

        user = User()

        user.id_number = data["id_number"]

        user.first_name = data["first_name"]

        user.last_name = data["last_name"]

        user.email = data["email"]

        user.phone = data["phone"]

        user.role = UserRole.CITIZEN

        user.status = UserStatus.ACTIVE

        user.set_password(data["password"])

        return self.repository.save(user)

    # ------------------------------------
    # LOGIN
    # ------------------------------------

    def login(self, username, password):

        user = self.repository.find_login_user(username)

        if not user:

            raise AuthenticationException(
                "Invalid username or password."
            )

        if not user.check_password(password):

            raise AuthenticationException(
                "Invalid username or password."
            )

        if user.status == UserStatus.LOCKED:

            raise AccountLockedException(
                "Account is locked."
            )

        if user.status == UserStatus.INACTIVE:

            raise AccountInactiveException(
                "Account is inactive."
            )

        access_token = create_access_token(

            identity=str(user.user_id),

            additional_claims={

                "role": user.role.value,

                "email": user.email
            }
        )

        refresh_token = create_refresh_token(

            identity=str(user.user_id)
        )

        return {

            "access_token": access_token,

            "refresh_token": refresh_token,

            "user": user.to_dict()

        }

    # ------------------------------------
    # REFRESH TOKEN
    # ------------------------------------

    def refresh(self):

        identity = get_jwt_identity()

        user = self.repository.find_by_id(identity)

        if not user:

            raise UserNotFoundException()

        token = create_access_token(

            identity=str(user.user_id),

            additional_claims={

                "role": user.role.value,

                "email": user.email

            }
        )

        return token

    # ------------------------------------
    # CURRENT USER
    # ------------------------------------

    def current_user(self):

        identity = get_jwt_identity()

        user = self.repository.find_by_id(identity)

        if not user:

            raise UserNotFoundException()

        if user.status == UserStatus.LOCKED:

            raise AccountLockedException("Account is locked.")

        if user.status == UserStatus.INACTIVE:

            raise AccountInactiveException("Account is inactive.")

        return user

    # ------------------------------------
    # CHANGE PASSWORD
    # ------------------------------------

    def change_password(

            self,

            current_password,

            new_password

    ):

        user = self.current_user()

        if not user.check_password(current_password):

            raise AuthenticationException(

                "Current password incorrect."

            )

        user.set_password(new_password)

        db.session.commit()

        return True