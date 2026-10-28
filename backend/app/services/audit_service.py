import uuid

from flask import request
from flask_jwt_extended import get_jwt_identity, get_jwt

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:

    def __init__(self):

        self.repository = AuditRepository()

    def log(

            self,

            action,

            entity,

            entity_id=None,

            description=None,

            old_value=None,

            new_value=None,

            status_code=200

    ):

        try:
            identity = get_jwt_identity()
            claims = get_jwt()
        except RuntimeError:
            identity = None
            claims = {}

        audit = AuditLog(

            user_id=claims.get("user_id") or identity or "SYSTEM",

            username=claims.get("email") or "SYSTEM",

            role=claims.get("role") or "SYSTEM",

            action=action,

            entity=entity,

            entity_id=str(entity_id) if entity_id else None,

            description=description,

            ip_address=request.remote_addr,

            request_method=request.method,

            endpoint=request.path,

            status_code=status_code,

            old_value=old_value,

            new_value=new_value,

            correlation_id=str(uuid.uuid4())

        )

        return self.repository.save(audit)

    def get_logs(self):

        return self.repository.find_all()

    def get_user_logs(self, user_id):

        return self.repository.find_by_user(user_id)

    def get_action_logs(self, action):

        return self.repository.find_by_action(action)

    def get_entity_logs(self, entity):

        return self.repository.find_by_entity(entity)