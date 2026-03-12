from pydantic import BaseModel

class SendRequest(BaseModel):
    phone:   str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [{"phone": "628123456789"}]
        }
    }

class NotifyResponse(BaseModel):
    status:        str
    phone:         str
    waha_response: dict
