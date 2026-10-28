from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

celery = Celery(
    "traffic_fines",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.update(

    timezone="Africa/Johannesburg",

    enable_utc=False,

    task_serializer="json",

    accept_content=["json"],

    result_serializer="json"

)

celery.conf.beat_schedule = {

    "daily-reminders": {

        "task": "app.tasks.scheduler_tasks.send_due_reminders",

        "schedule": crontab(hour=8, minute=0)

    },

    "overdue-reminders": {

        "task": "app.tasks.scheduler_tasks.send_overdue_notifications",

        "schedule": crontab(hour=9, minute=0)

    },

    "retry-failed": {

        "task": "app.tasks.scheduler_tasks.retry_failed_notifications",

        "schedule": crontab(minute="*/15")

    },

    "cleanup-notifications": {

        "task": "app.tasks.scheduler_tasks.cleanup_notifications",

        "schedule": crontab(hour=2, minute=0)

    },

    "weekly-report": {

        "task": "app.tasks.scheduler_tasks.weekly_summary",

        "schedule": crontab(
            day_of_week="monday",
            hour=7,
            minute=0
        )

    },

    "monthly-report": {

        "task": "app.tasks.scheduler_tasks.monthly_statistics",

        "schedule": crontab(
            day_of_month=1,
            hour=6,
            minute=0
        )

    }

}

celery.conf.task_queues = (

    Queue(

        "notifications",

        Exchange("notifications"),

        routing_key="notifications"

    ),

    Queue(

        "emails",

        Exchange("emails"),

        routing_key="emails"

    ),

    Queue(

        "sms",

        Exchange("sms"),

        routing_key="sms"

    ),

    Queue(

        "whatsapp",

        Exchange("whatsapp"),

        routing_key="whatsapp"

    )

)