class NotificationException(Exception):
    pass


class NotificationNotFoundException(NotificationException):
    pass


class NotificationDeliveryException(NotificationException):
    pass


class InvalidNotificationException(NotificationException):
    pass


class TemplateNotFoundException(NotificationException):
    pass


class NotificationChannelException(NotificationException):
    pass