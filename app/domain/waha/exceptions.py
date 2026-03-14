class WahaDomainError(Exception):
    """Base WAHA domain error."""

class WahaSessionNotAuthenticated(WahaDomainError):
    """WAHA session is not authenticated in domain logic."""

class WahaMessageFailed(WahaDomainError):
    """WAHA message failed to send in domain logic."""
