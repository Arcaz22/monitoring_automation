from datetime import datetime

from pydantic import BaseModel


class WahaMessageDTO(BaseModel):
    chat_id: str
    text: str
    sent_at: str
    status: str

class SendTestRequest(BaseModel):
    phone: str | None = None

    model_config = {
        "json_schema_extra": {"examples": [{"phone": "628123456789"}]}
    }


class TrelloNotifyRequest(BaseModel):
    board_id:      str | None = None
    dry_run:       bool       = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"dry_run": False},
                {"board_id": "69821a7c416e3bb3d7300e1a", "dry_run": True},
            ]
        }
    }

class SendTestResponse(BaseModel):
    status:        str
    phone:         str
    waha_response: WahaMessageDTO


class NotificationResult(BaseModel):
    recipient_name: str
    recipient_wa:   str
    card_name:      str
    type:           str
    sent:           bool
    error:          str | None = None


class TrelloNotifyResponse(BaseModel):
    status:        str
    dry_run:       bool
    total_cards:   int
    total_sent:    int
    total_failed:  int
    results:       list[NotificationResult]
    triggered_at:  datetime
