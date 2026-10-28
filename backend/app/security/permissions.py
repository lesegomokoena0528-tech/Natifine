from app.models.user import UserRole


class Permission:

    @staticmethod
    def is_admin(user):

        return user.role == UserRole.ADMIN

    @staticmethod
    def is_officer(user):

        return user.role == UserRole.OFFICER

    @staticmethod
    def is_citizen(user):

        return user.role == UserRole.CITIZEN

    @staticmethod
    def can_issue_fines(user):

        return user.role in [

            UserRole.ADMIN,

            UserRole.OFFICER

        ]

    @staticmethod
    def can_manage_users(user):

        return user.role == UserRole.ADMIN

    @staticmethod
    def can_view_reports(user):

        return user.role in [

            UserRole.ADMIN,

            UserRole.OFFICER

        ]

    @staticmethod
    def can_pay_fines(user):

        return user.role == UserRole.CITIZEN

    @staticmethod
    def can_dispute(user):

        return user.role == UserRole.CITIZEN