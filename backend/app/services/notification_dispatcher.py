class NotificationDispatcher:

    @staticmethod
    def queue(notification_id):
        """
        Queue a notification for asynchronous delivery.

        In production a Celery/Redis broker handles delivery. When the broker
        is not available (e.g. during an academic demonstration where Redis is
        not running) the task is executed synchronously so that notifications
        are still recorded and delivered rather than lost.
        """

        from app.tasks.notification_tasks import send_notification_task

        try:
            send_notification_task.delay(notification_id)
        except Exception:
            try:
                send_notification_task.apply(args=[notification_id])
            except Exception:
                pass