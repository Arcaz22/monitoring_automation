import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.trello.client import TrelloClient


async def main() -> None:
    client = TrelloClient()
    try:
        boards = await client.get_boards()

        print(f"\n{'='*62}")
        print(f"  TRELLO OVERVIEW  —  {len(boards)} board(s) found")
        print(f"{'='*62}")

        for board in boards:
            print(f"\n📋 BOARD : {board.name}")
            print(f"   ID    : {board.id}")
            print(f"   {'─'*54}")

            # Members
            members = await client.get_board_members(board.id)
            member_map = {m.id: m for m in members}

            print(f"\n   👥 MEMBERS ({len(members)}):")
            for m in members:
                print(f"      • {m.fullname:<22} @{m.username:<22} id: {m.id}")

            # Cards
            cards = await client.get_board_cards(board.id, board.name)
            print(f"\n   🃏 ACTIVE CARDS ({len(cards)}):")

            if not cards:
                print("      (no active cards in To Do / Doing)")
                continue

            for card in cards:
                assigned = [
                    f"@{member_map[mid].username}"
                    if mid in member_map else f"(unknown:{mid})"
                    for mid in card.member_ids
                ]
                days_ago = (datetime.now(timezone.utc) - card.last_activity).days

                print(f"\n      📌 {card.name}")
                print(f"         List        : {card.list_name}")
                print(f"         Assigned    : {', '.join(assigned) or '(unassigned)'}")
                print(f"         Last active : {days_ago} day(s) ago")
                print(f"         URL         : {card.url}")

        print(f"\n{'='*62}")
        print("  Copy the @usernames above → data/mapping.json")
        print(f"{'='*62}\n")

    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
