from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class TrelloBoard:
    id: str
    name: str


@dataclass(frozen=True)
class TrelloMember:
    id: str
    username: str
    fullname: str


@dataclass(frozen=True)
class TrelloCard:
    id: str
    name: str
    list_name: str
    board_name: str
    member_ids: list[str]
    last_activity: datetime
    url: str


class NotificationType(str, Enum):
    TODO_REMINDER = "todo_reminder"
    DEADLINE_PASSED = "deadline_passed"


@dataclass(frozen=True)
class CardNotification:
    type: NotificationType
    recipient_wa: str
    recipient_name: str
    card_name: str
    card_url: str
    list_name: str
    days_stagnant: int
    board_name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
