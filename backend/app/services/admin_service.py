from datetime import datetime
import secrets
import string

from sqlalchemy.exc import IntegrityError

from app.config.database import db

from app.repositories.admin_repository import AdminRepository
from app.repositories.user_repository import UserRepository

from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService

from app.models.user import User


class AdminService:

    def __init__(self):

        self.repository = AdminRepository()

        self.user_repository = UserRepository()

        self.notification_service = NotificationService()

        self.audit_service = AuditService()

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard(self):

        return self.repository.dashboard_statistics()

    # =====================================================
    # USERS
    # =====================================================

    def all_users(self):

        return self.repository.get_all_users()

    def get_user(self, user_id):

        user = self.repository.get_user_by_id(user_id)

        if user is None:
            raise ValueError("User not found.")

        return user

    def search_users(self, keyword):

        return self.repository.search_users(keyword)

    # =====================================================
    # CREATE USER
    # =====================================================

    def create_user(

            self,

            first_name,

            last_name,

            email,

            phone,

            id_number,

            password,

            role

    ):

        existing = self.user_repository.find_by_email(email)

        if existing:

            raise ValueError(
                "Email already exists."
            )

        if self.user_repository.find_by_phone(phone):

            raise ValueError(
                "Phone number already exists."
            )

        if self.user_repository.find_by_id_number(id_number):

            raise ValueError(
                "ID number already exists."
            )

        user = User()

        user.first_name = first_name

        user.last_name = last_name

        user.email = email

        user.phone = phone

        user.id_number = id_number

        user.set_password(password)
        from app.models.user import UserRole, UserStatus
        try:
            user.role = UserRole[role.upper()] if isinstance(role, str) else role
        except Exception:
            try:
                user.role = role.value if hasattr(role, 'value') else role
            except Exception:
                user.role = role
        user.status = UserStatus.ACTIVE

        self.repository.save_user(user)

        try:

            self.notification_service.send_welcome_email(user)

        except Exception:

            pass

        self.audit_service.log(

            action="CREATE_USER",

            entity="User",

            entity_id=user.user_id,

            description=f"Created {email}"

        )

        return user

    # =====================================================
    # UPDATE USER
    # =====================================================

    def update_user(

            self,

            user_id,

            data

    ):

        user = self.get_user(user_id)

        for key, value in data.items():

            setattr(user, key, value)

        self.repository.save_user(user)

        self.audit_service.log(

            action="UPDATE_USER",

            entity="User",

            entity_id=user.user_id,

            description=f"Updated {user.email}"

        )

        return user

    # =====================================================
    # DELETE USER
    # =====================================================

    def delete_user(self, user_id):

        user = self.get_user(user_id)

        email = user.email

        dependencies = self.repository.user_dependency_counts(user_id)

        if any(dependencies.values()):

            raise ValueError(
                "This account has linked fines, payments or disputes and "
                "cannot be permanently deleted. Deactivate it instead."
            )

        try:

            self.repository.delete_user(user)

        except IntegrityError:

            db.session.rollback()

            raise ValueError(
                "This account has related records and cannot be permanently "
                "deleted. Deactivate it instead."
            )

        self.audit_service.log(

            action="DELETE_USER",

            entity="User",

            entity_id=user_id,

            description=f"Deleted {email}"

        )

    # =====================================================
    # ACTIVATE
    # =====================================================

    def activate_user(self, user_id):

        user = self.get_user(user_id)

        from app.models.user import UserStatus
        user.status = UserStatus.ACTIVE

        self.repository.save_user(user)

        self.audit_service.log(

            action="ACTIVATE_USER",

            entity="User",

            entity_id=user.user_id,

            description=user.email

        )

        return user

    # =====================================================
    # DEACTIVATE
    # =====================================================

    def deactivate_user(self, user_id):

        user = self.get_user(user_id)

        from app.models.user import UserStatus
        user.status = UserStatus.INACTIVE

        self.repository.save_user(user)

        self.audit_service.log(

            action="SUSPEND_USER",

            entity="User",

            entity_id=user.user_id,

            description=user.email

        )

        return user

    # =====================================================
    # CHANGE ROLE
    # =====================================================

    def assign_role(

            self,

            user_id,

            role

    ):

        user = self.get_user(user_id)

        user.role = role

        self.repository.save_user(user)

        self.audit_service.log(

            action="ROLE_CHANGED",

            entity="User",

            entity_id=user.user_id,

            description=f"{user.email} -> {role}"

        )

        return user

    # =====================================================
    # PASSWORD RESET
    # =====================================================

    def reset_password(self, user_id):

        user = self.get_user(user_id)

        password = self.generate_password()

        user.set_password(password)

        self.repository.save_user(user)

        self.notification_service.password_reset(

            user,

            password

        )

        self.audit_service.log(

            action="PASSWORD_RESET",

            entity="User",

            entity_id=user.user_id,

            description=user.email

        )

        return {

            "temporary_password": password

        }

    # =====================================================
    # OFFICERS
    # =====================================================

    def officers(self):

        return self.repository.get_all_officers()

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self):

        return self.repository.dashboard_statistics()

    # =====================================================
    # PASSWORD GENERATOR
    # =====================================================

    @staticmethod
    def generate_password(length=12):

        alphabet = (

            string.ascii_letters +

            string.digits +

            "!@#$%^&*"

        )

        return "".join(

            secrets.choice(alphabet)

            for _ in range(length)

        )