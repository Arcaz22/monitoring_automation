from app.core.exceptions import AppException


class TrelloError(AppException):
    """Raised when Trello API returns a non-2xx response."""


class TrelloBoardNotFound(AppException):
    """Raised when a requested board ID does not exist."""
