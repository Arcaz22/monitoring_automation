import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from app.application.usecases.notification_builder import NotificationBuilderUseCase
from app.core.settings import get_settings
from app.domain.guardian.entities import GuardianRunResult, NotificationResult
from app.domain.trello.entities import TrelloCard
from app.domain.waha.entities import WahaMessage
from app.infrastructure.trello.client import TrelloClient
from app.infrastructure.waha.client import WAHAClient

logger = logging.getLogger(__name__)


class GuardianUseCase:
    def __init__(
        self,
        waha: WAHAClient,
        trello: TrelloClient | None = None,
    ) -> None:
        self._waha = waha
        self._trello = trello
        self._builder = NotificationBuilderUseCase()
        self._settings = get_settings()

        self._send_delay_seconds = 2.0

        mapping_path = Path("data/mapping.json")
        if mapping_path.exists():
            with open(mapping_path) as f:
                self._member_map = json.load(f)
        else:
            self._member_map = {}

    async def run(self, dry_run: bool = False, board_id: str | None = None) -> GuardianRunResult:

        if not self._trello:
            raise RuntimeError("GuardianUseCase.run() requires trello dependency")

        bid = board_id or self._settings.trello_board_id
        logger.info("[Guardian] Starting run — board: %s, dry_run: %s", bid, dry_run)

        board_name = "Trello Board"

        cards = await self._trello.get_board_cards(bid, board_name)

        todo_cards, doing_cards = self._builder.build(cards)

        all_cards = todo_cards + doing_cards

        result = GuardianRunResult(
            dry_run=dry_run,
            total_cards=len(cards),
            total_sent=0,
            total_failed=0,
        )

        triggered_at = result.triggered_at.astimezone(
            ZoneInfo("Asia/Jakarta")
        ).strftime("%Y-%m-%d %H:%M:%S")

        member_cards: dict[str, list[TrelloCard]] = {}

        for card in all_cards:
            if not card.member_ids:
                continue

            for member_id in card.member_ids:
                member_cards.setdefault(member_id, []).append(card)

        for member_id, cards in member_cards.items():

            if member_id not in self._member_map:
                logger.warning("No WA mapping for member %s", member_id)
                continue

            member = self._member_map[member_id]

            phone = member["phone"]
            name = member["name"]

            message = self._format_summary(
                board_name=board_name,
                triggered_at=triggered_at,
                cards=cards,
                recipient_name=name,
            )

            if dry_run:
                logger.info("[DRY RUN] Would send summary to %s", phone)
                sent = True
                error = None
            else:
                try:
                    await self._waha.send_text(phone, message)
                    sent = True
                    error = None
                except Exception as e:
                    sent = False
                    error = str(e)

            result.results.append(
                NotificationResult(
                    recipient_name=name,
                    recipient_wa=phone,
                    card_name="Summary",
                    type="SUMMARY",
                    sent=sent,
                    error=error,
                )
            )

            if sent:
                result.total_sent += 1
            else:
                result.total_failed += 1

            await asyncio.sleep(self._send_delay_seconds)

        logger.info(
            "[Guardian] Done — sent: %d, failed: %d",
            result.total_sent,
            result.total_failed,
        )

        return result

    async def send_hello(self, phone: str | None = None) -> WahaMessage:

        target = phone or self._settings.test_phone
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = (
            "🤖 *Rampung Space* — Hello Testing!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ WAHA connection is *working*.\n"
            f"🕐 Sent at: {now}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "_This message was triggered by the Guardian cron job._"
        )

        logger.info("[Guardian] Sending hello to %s", target)

        resp = await self._waha.send_text(target, message)

        return WahaMessage(
            chat_id=f"{target}@c.us" if "@" not in target else target,
            text=message,
            sent_at=now,
            status=str(resp.get("status", "sent")),
        )

    @staticmethod
    def _format_summary(
        *,
        board_name: str,
        triggered_at: str,
        cards: list[TrelloCard],
        recipient_name: str,
    ) -> str:

        lines = [
            "🤖 *Rampung Space — Summary*",
            "━━━━━━━━━━━━━━━━━━━━━━━",
            f"👤 {recipient_name}",
            f"📋 Board: *{board_name}*",
            f"🕐 Triggered at: {triggered_at}",
            "",
        ]

        if not cards:
            lines.append("✅ Tidak ada card yang perlu diingatkan.")
        else:
            doing_cards = [c for c in cards if "doing" in c.list_name.lower()]
            todo_cards = [c for c in cards if "to do" in c.list_name.lower() or "todo" in c.list_name.lower()]
            other_cards = [c for c in cards if c not in todo_cards and c not in doing_cards]

            if doing_cards:
                lines.append("🔄 *Sedang Dikerjakan (Doing)*")
                for idx, card in enumerate(doing_cards, start=1):
                    lines.append(f"  {idx}. *{card.name}*")
                    if card.url:
                        lines.append(f"      🔗 {card.url}")
                lines.append("")

            if todo_cards:
                lines.append("📌 *Belum Dikerjakan (To Do)*")
                for idx, card in enumerate(todo_cards, start=1):
                    lines.append(f"  {idx}. *{card.name}*")
                    if card.url:
                        lines.append(f"      🔗 {card.url}")
                lines.append("")

            if other_cards:
                lines.append("📋 *Lainnya*")
                for idx, card in enumerate(other_cards, start=1):
                    lines.append(f"  {idx}. *{card.name}* ({card.list_name})")
                    if card.url:
                        lines.append(f"      🔗 {card.url}")
                lines.append("")

        total = len(cards)
        doing_count = sum(1 for c in cards if "doing" in c.list_name.lower())
        todo_count = sum(1 for c in cards if "to do" in c.list_name.lower() or "todo" in c.list_name.lower())

        lines.append(f"📊 Total: *{total} card* | 🔄 {doing_count} doing · 📌 {todo_count} to do")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━")

        return "\n".join(lines)
