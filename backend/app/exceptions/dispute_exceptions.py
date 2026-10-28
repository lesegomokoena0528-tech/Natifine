class DisputeException(Exception):
    """Base Dispute Exception"""
    pass


class DisputeNotFoundException(DisputeException):
    pass


class DuplicateDisputeException(DisputeException):
    pass


class InvalidDisputeException(DisputeException):
    pass


class DocumentUploadException(DisputeException):
    pass


class InvalidDocumentException(DisputeException):
    pass


class ReviewException(DisputeException):
    pass