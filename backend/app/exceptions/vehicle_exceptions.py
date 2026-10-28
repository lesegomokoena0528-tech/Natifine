class VehicleException(Exception):
    """Base vehicle exception."""
    pass


class VehicleNotFoundException(VehicleException):
    pass


class DuplicateRegistrationException(VehicleException):
    pass


class DuplicateVINException(VehicleException):
    pass


class DuplicateEngineNumberException(VehicleException):
    pass


class InvalidVehicleOwnerException(VehicleException):
    pass


class VehicleAlreadyAssignedException(VehicleException):
    pass