import logging
from datetime import datetime

from app.core.settings import get_settings
from app.infrastructure.waha.client import WAHAClient

logger = logging.getLogger(__name__)


class GuardianUseCase:
    def __init__(self, waha: WAHAClient) -> None:
        self._waha = waha

    async def send_hello(self, phone: str | None = None) -> dict:
        target = phone or get_settings().test_phone
        now    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = (
            "🤖 *Project Guardian* — Hello Testing!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ WAHA connection is *working*.\n"
            f"🕐 Sent at: {now}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "_This message was triggered by the Guardian cron job._"
        )

        logger.info("[Guardian] Sending hello to %s", target)
        result = await self._waha.send_text(target, message)
        logger.info("[Guardian] Sent OK → %s", result)
        return result
