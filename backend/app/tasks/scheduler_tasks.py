from app.config.celery import celery

from app.services.scheduler_service import SchedulerService


service = SchedulerService()


@celery.task
def send_due_reminders():

    return service.send_due_reminders()


@celery.task
def send_overdue_notifications():

    return service.send_overdue_notifications()


@celery.task
def retry_failed_notifications():

    return service.retry_failed_notifications()


@celery.task
def cleanup_notifications():

    return service.cleanup_old_notifications()


@celery.task
def monthly_statistics():

    return service.generate_monthly_statistics()


@celery.task
def weekly_summary():

    return service.weekly_summary()