class FineException(Exception):
    """Base Fine Exception"""
    pass


class FineNotFoundException(FineException):
    pass


class DuplicateFineException(FineException):
    pass


class InvalidOfficerException(FineException):
    pass


class InvalidVehicleException(FineException):
    pass


class InvalidFineStatusException(FineException):
    pass


class FineAlreadyPaidException(FineException):
    pass


class FineAlreadyCancelledException(FineException):
    pass


class EvidenceUploadException(FineException):
    pass