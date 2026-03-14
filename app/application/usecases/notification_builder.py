import logging
from datetime import datetime, timezone

from app.domain.trello.entities import TrelloCard

logger = logging.getLogger(__name__)

TODO_STAGNANT_DAYS = 0
DOING_STAGNANT_DAYS = 0


class NotificationBuilderUseCase:
    def build(self, cards: list[TrelloCard]) -> tuple[list[TrelloCard], list[TrelloCard]]:
        todo_cards: list[TrelloCard] = []
        doing_cards: list[TrelloCard] = []

        for card in cards:
            list_lower = card.list_name.lower()
            days_stagnant = self._days_stagnant(card)

            if list_lower.startswith("done"):
                continue

            if list_lower == "to do" and days_stagnant >= TODO_STAGNANT_DAYS:
                todo_cards.append(card)

            if list_lower.startswith("doing") and days_stagnant >= DOING_STAGNANT_DAYS:
                doing_cards.append(card)

        logger.info(
            len(todo_cards),
            len(doing_cards),
        )
        return todo_cards, doing_cards

    @staticmethod
    def _days_stagnant(card: TrelloCard) -> int:
        return (datetime.now(timezone.utc) - card.last_activity).days
