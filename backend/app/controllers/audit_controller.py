from app.services.audit_service import AuditService
from app.utils.response import success_response

class AuditController:

    def __init__(self):

        self.service = AuditService()

    def get_logs(self):

        logs = self.service.get_logs()

        return success_response(

            "Audit logs retrieved",

            [log.to_dict() for log in logs]

        )

    def user_logs(self, user_id):

        logs = self.service.get_user_logs(user_id)

        return success_response(

            "User audit logs",

            [log.to_dict() for log in logs]

        )

    def action_logs(self, action):

        logs = self.service.get_action_logs(action)

        return success_response(

            "Action audit logs",

            [log.to_dict() for log in logs]

        )

    def entity_logs(self, entity):

        logs = self.service.get_entity_logs(entity)

        return success_response(

            "Entity audit logs",

            [log.to_dict() for log in logs]

        )