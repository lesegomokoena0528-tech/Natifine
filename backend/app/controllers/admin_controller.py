from flask import request

from app.services.admin_service import AdminService
from app.services.report_service import ReportService

from app.schemas.admin_schema import (
    CreateUserSchema,
    UpdateUserSchema
)

from app.utils.response import (
    success_response,
    error_response
)

from app.services.export_service import ExportService

export_service = ExportService()


class AdminController:

    def __init__(self):

        self.admin_service = AdminService()

        self.report_service = ReportService()

        self.create_schema = CreateUserSchema()

        self.update_schema = UpdateUserSchema()

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard(self):

        try:

            dashboard = self.admin_service.dashboard()

            return success_response(

                "Dashboard retrieved successfully",

                dashboard

            )

        except Exception as ex:

            return error_response(str(ex), 500)

    # =====================================================
    # SYSTEM STATISTICS
    # =====================================================

    def statistics(self):

        try:

            return success_response(

                "Statistics retrieved",

                self.admin_service.statistics()

            )

        except Exception as ex:

            return error_response(str(ex), 500)

    # =====================================================
    # GET ALL USERS
    # =====================================================

    def get_users(self):

        try:

            users = self.admin_service.all_users()

            return success_response(

                "Users retrieved successfully",

                [user.to_dict() for user in users]

            )

        except Exception as ex:

            return error_response(str(ex), 500)

    # =====================================================
    # GET USER
    # =====================================================

    def get_user(self, user_id):

        try:

            user = self.admin_service.get_user(user_id)

            return success_response(

                "User retrieved",

                user.to_dict()

            )

        except Exception as ex:

            return error_response(str(ex), 404)

    # =====================================================
    # SEARCH USERS
    # =====================================================

    def search_users(self):

        try:

            keyword = request.args.get(

                "keyword",

                ""

            )

            users = self.admin_service.search_users(

                keyword

            )

            return success_response(

                "Search completed",

                [u.to_dict() for u in users]

            )

        except Exception as ex:

            return error_response(str(ex), 400)

    # =====================================================
    # CREATE USER
    # =====================================================

    def create_user(self):

        try:

            data = self.create_schema.load(

                request.get_json()

            )

            user = self.admin_service.create_user(

                first_name=data["first_name"],

                last_name=data["last_name"],

                email=data["email"],

                phone=data["phone"],

                id_number=data["id_number"],

                password=data["password"],

                role=data["role"]

            )

            return success_response(

                "User created successfully",

                user.to_dict(),

                201

            )

        except ValueError as ex:

            return error_response(str(ex), 409)

        except Exception as ex:

            return error_response(str(ex), 400)

    # =====================================================
    # UPDATE USER
    # =====================================================

    def update_user(self, user_id):

        try:

            data = self.update_schema.load(

                request.get_json()

            )

            user = self.admin_service.update_user(

                user_id,

                data

            )

            return success_response(

                "User updated",

                user.to_dict()

            )

        except Exception as ex:

            return error_response(str(ex), 400)

    # =====================================================
    # DELETE USER
    # =====================================================

    def delete_user(self, user_id):

        try:

            self.admin_service.delete_user(user_id)

            return success_response(

                "User deleted"

            )

        except ValueError as ex:

            return error_response(str(ex), 409)

        except Exception as ex:

            return error_response(str(ex), 400)

    # =====================================================
    # ACTIVATE USER
    # =====================================================

    def activate_user(self, user_id):

        try:

            user = self.admin_service.activate_user(

                user_id

            )

            return success_response(

                "User activated",

                user.to_dict()

            )

        except Exception as ex:

            return error_response(str(ex), 400)

    # =====================================================
    # DEACTIVATE USER
    # =====================================================

    def deactivate_user(self, user_id):

        try:

            user = self.admin_service.deactivate_user(

                user_id

            )

            return success_response(

                "User suspended",

                user.to_dict()

            )

        except Exception as ex:

            return error_response(str(ex), 400)

    # =====================================================
    # ASSIGN ROLE
    # =====================================================

    def assign_role(self, user_id):

        try:

            data = request.get_json()

            user = self.admin_service.assign_role(

                user_id,

                data["role"]

            )

            return success_response(

                "Role updated",

                user.to_dict()

            )

        except Exception as ex:

            return error_response(str(ex), 400)

    # =====================================================
    # RESET PASSWORD
    # =====================================================

    def reset_password(self, user_id):

        try:

            result = self.admin_service.reset_password(

                user_id

            )

            return success_response(

                "Password reset successfully",

                result

            )

        except Exception as ex:

            return error_response(str(ex), 400)

    # =====================================================
    # GET OFFICERS
    # =====================================================

    def officers(self):

        try:

            officers = self.admin_service.officers()

            return success_response(

                "Officers retrieved",

                [

                    officer.to_dict()

                    for officer in officers

                ]

            )

        except Exception as ex:

            return error_response(str(ex), 500)

    # =====================================================
    # REPORTS
    # =====================================================

    def dashboard_report(self):

        return success_response(

            "Dashboard report",

            self.report_service.dashboard_report()

        )

    def revenue_report(self):

        return success_response(

            "Revenue report",

            self.report_service.revenue_report()

        )

    def fine_report(self):

        return success_response(

            "Fine report",

            self.report_service.fine_report()

        )

    def vehicle_report(self):

        return success_response(

            "Vehicle report",

            self.report_service.vehicle_report()

        )

    def dispute_report(self):

        return success_response(

            "Dispute report",

            self.report_service.dispute_report()

        )

    def notification_report(self):

        return success_response(

            "Notification report",

            self.report_service.notification_report()

        )
    def full_system_report(self):

        return success_response(

            "System report",

            self.report_service.full_system_report()

        )

    # =====================================================
    # EXPORT REPORT
    # =====================================================

    def export_report(self):

        report = self.report_service.full_system_report()

        format = request.args.get(

            "format",

            "pdf"

        )

        if format == "pdf":

            return export_service.export_pdf(

                "system_report",

                report

            )

        if format == "excel":

            return export_service.export_excel(

                "system_report",

                report

            )

        if format == "csv":

            return export_service.export_csv(

                "system_report",

                report

            )

        return {

            "error": "Unsupported format"

        }, 400