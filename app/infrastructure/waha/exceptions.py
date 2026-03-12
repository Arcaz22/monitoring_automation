from app.core.exceptions import AppException

class WAHAError(AppException):
    """WAHA returned a non-200 response."""

class SessionNotAuthenticated(AppException):
    """WAHA session is not yet AUTHENTICATED."""
