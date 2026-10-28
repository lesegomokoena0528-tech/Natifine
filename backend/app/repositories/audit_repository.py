from app.config.database import db
from app.models.audit_log import AuditLog


class AuditRepository:

    def save(self, audit):

        db.session.add(audit)
        db.session.commit()

        return audit

    def find_all(self):

        return AuditLog.query.order_by(

            AuditLog.created_at.desc()

        ).all()

    def find_by_user(self, user_id):

        return AuditLog.query.filter_by(

            user_id=user_id

        ).order_by(

            AuditLog.created_at.desc()

        ).all()

    def find_by_action(self, action):

        return AuditLog.query.filter_by(

            action=action

        ).order_by(

            AuditLog.created_at.desc()

        ).all()

    def find_by_entity(self, entity):

        return AuditLog.query.filter_by(

            entity=entity

        ).order_by(

            AuditLog.created_at.desc()

        ).all()

    def find_by_correlation_id(self, correlation_id):

        return AuditLog.query.filter_by(

            correlation_id=correlation_id

        ).first()