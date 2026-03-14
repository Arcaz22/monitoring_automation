import httpx

from app.core.settings import get_settings
from app.infrastructure.waha.exceptions import SessionNotAuthenticated, WAHAError


class WAHAClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._settings.waha_api_key:
            headers["X-Api-Key"] = self._settings.waha_api_key

        self._http = httpx.AsyncClient(
            base_url=self._settings.waha_base_url,
            headers=headers,
            timeout=15.0,
        )

    async def send_text(self, phone: str, message: str) -> dict:
        status = await self.session_status()
        if status not in ("AUTHENTICATED", "WORKING"):
            raise SessionNotAuthenticated(
                f"WAHA session '{self._settings.waha_session}' is not AUTHENTICATED "
                f"(current: {status}). Scan the QR code first."
            )

        chat_id = phone if "@" in phone else f"{phone}@c.us"
        payload = {
            "session": self._settings.waha_session,
            "chatId":  chat_id,
            "text":    message,
        }

        resp = await self._http.post("/api/sendText", json=payload)
        if resp.status_code not in (200, 201):
            raise WAHAError(f"WAHA {resp.status_code}: {resp.text}")

        return resp.json() if resp.content else {"status": "sent"}


    async def health_check(self) -> bool:
        try:
            r = await self._http.get("/api/version")
            return r.status_code == 200
        except Exception:
            return False

    async def session_status(self) -> str:
        try:
            r = await self._http.get(f"/api/sessions/{self._settings.waha_session}")
            return r.json().get("status", "UNKNOWN")
        except Exception:
            return "ERROR"

    async def aclose(self) -> None:
        await self._http.aclose()
