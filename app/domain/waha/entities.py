from dataclasses import dataclass

@dataclass
class WahaMessage:
    chat_id: str
    text: str
    sent_at: str
    status: str

@dataclass
class WahaSession:
    name: str
    status: str
    me_id: str
    push_name: str

@dataclass
class WahaError:
    code: int
    message: str
    details: str = ""
