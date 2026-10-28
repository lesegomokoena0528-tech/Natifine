class AuthenticationException(Exception):
    """Raised when authentication fails."""
    pass


class AuthorizationException(Exception):
    """Raised when user is not authorized."""
    pass


class DuplicateUserException(Exception):
    """Raised when duplicate user exists."""
    pass


class UserNotFoundException(Exception):
    """Raised when user cannot be found."""
    pass


class AccountLockedException(Exception):
    """Raised when account is locked."""
    pass


class AccountInactiveException(Exception):
    """Raised when account is inactive."""
    pass