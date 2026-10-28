from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger

from app.config.celery import celery

logger = get_task_logger(__name__)


# =====================================================
# Send Notification
# =====================================================

@celery.task(
    bind=True,
    name="notification.send",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_kwargs={"max_retries": 5},
    retry_jitter=True
)
def send_notification_task(self, notification_id):

    from app.services.notification_service import NotificationService

    service = NotificationService()

    logger.info(
        "Processing notification %s",
        notification_id
    )

    try:

        service.send_notification(notification_id)

        logger.info(
            "Notification %s completed.",
            notification_id
        )

    except MaxRetriesExceededError:

        logger.error(
            "Maximum retries exceeded for %s",
            notification_id
        )

        raise

    except Exception as ex:

        logger.exception(ex)

        raise


# =====================================================
# Bulk Notifications
# =====================================================

@celery.task(
    name="notification.bulk"
)
def bulk_notification_task(notification_ids):

    from app.services.notification_service import NotificationService

    service = NotificationService()

    results = []

    for notification_id in notification_ids:

        try:

            service.send_notification(notification_id)

            results.append({

                "notification": notification_id,

                "status": "SUCCESS"

            })

        except Exception as ex:

            logger.exception(ex)

            results.append({

                "notification": notification_id,

                "status": "FAILED",

                "reason": str(ex)

            })

    return results


# =====================================================
# Retry Failed
# =====================================================

@celery.task(
    name="notification.retry"
)
def retry_failed_notifications():

    from app.services.notification_service import NotificationService

    service = NotificationService()

    return service.retry_failed()


# =====================================================
# Dead Letter Queue
# =====================================================

@celery.task(
    name="notification.dead_letter"
)
def dead_letter_notification(
    notification_id,
    reason
):

    logger.error(

        "Dead Letter Queue | Notification=%s | Reason=%s",

        notification_id,

        reason

    )

    return {

        "notification": notification_id,

        "reason": reason

    }


# =====================================================
# Queue Routing
# =====================================================

celery.conf.task_routes = {

    "notification.send": {

        "queue": "notifications"

    },

    "notification.bulk": {

        "queue": "notifications"

    },

    "notification.retry": {

        "queue": "notifications"

    },

    "notification.dead_letter": {

        "queue": "notifications"

    }

}