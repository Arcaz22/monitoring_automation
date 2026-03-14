from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class NotificationResult:
    recipient_name: str
    recipient_wa:   str
    card_name:      str
    type:           str
    sent:           bool
    error:          str | None = None


@dataclass
class GuardianRunResult:
    dry_run:      bool
    total_cards:  int
    total_sent:   int
    total_failed: int
    results:      list[NotificationResult] = field(default_factory=list)
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
