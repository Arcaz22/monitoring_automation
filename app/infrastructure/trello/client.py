from datetime import datetime

import httpx
from app.core.settings import get_settings
from app.domain.trello.entities import TrelloBoard, TrelloCard, TrelloMember
from app.infrastructure.trello.exceptions import TrelloError

MONITORED_LISTS = ("to do", "doing")


class TrelloClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._auth = {
            "key":   self._settings.trello_api_key,
            "token": self._settings.trello_token,
        }
        self._http = httpx.AsyncClient(
            base_url="https://api.trello.com/1",
            headers={"Content-Type": "application/json"},
            timeout=15.0,
        )

    async def _get_list_map(self, board_id: str) -> dict[str, str]:
        resp = await self._http.get(f"/boards/{board_id}/lists", params={
            **self._auth,
            "fields": "id,name",
            "filter": "open",
        })
        self._raise_for_status(resp)
        return {l["id"]: l["name"] for l in resp.json()}

    @staticmethod
    def _raise_for_status(resp: httpx.Response) -> None:
        if resp.status_code not in range(200, 300):
            raise TrelloError(f"Trello API error {resp.status_code}: {resp.text}")

    @staticmethod
    def _is_monitored(list_name: str) -> bool:
        """Return True if the list should be monitored by Guardian."""
        lower = list_name.lower()
        return any(lower.startswith(prefix) for prefix in MONITORED_LISTS)

    async def get_boards(self) -> list[TrelloBoard]:
        resp = await self._http.get("/members/me/boards", params={
            **self._auth,
            "fields": "id,name",
            "filter": "open",
        })
        self._raise_for_status(resp)
        return [TrelloBoard(id=b["id"], name=b["name"]) for b in resp.json()]

    async def get_board_members(self, board_id: str) -> list[TrelloMember]:
        resp = await self._http.get(f"/boards/{board_id}/members", params={
            **self._auth,
            "fields": "id,username,fullName",
        })
        self._raise_for_status(resp)
        return [
            TrelloMember(
                id=m["id"],
                username=m["username"],
                fullname=m.get("fullName", ""),
            )
            for m in resp.json()
        ]

    async def get_board_lists(self, board_id: str) -> list[dict]:
        resp = await self._http.get(f"/boards/{board_id}/lists", params={
            **self._auth,
            "fields": "id,name",
            "filter": "open",
        })
        self._raise_for_status(resp)
        return resp.json()

    async def get_board_cards(self, board_id: str, board_name: str) -> list[TrelloCard]:
        """
        Fetch open cards from a board.
        Only returns cards in monitored lists: To Do, Doing - X.
        """
        list_map = await self._get_list_map(board_id)
        resp = await self._http.get(f"/boards/{board_id}/cards", params={
            **self._auth,
            "fields": "id,name,idList,idMembers,dateLastActivity,url",
            "filter": "open",
        })
        self._raise_for_status(resp)

        cards = []
        for c in resp.json():
            list_name = list_map.get(c["idList"], "Unknown")
            if not self._is_monitored(list_name):
                continue
            cards.append(TrelloCard(
                id=c["id"],
                name=c["name"],
                list_name=list_name,
                board_name=board_name,
                member_ids=c.get("idMembers", []),
                last_activity=datetime.fromisoformat(
                    c["dateLastActivity"].replace("Z", "+00:00")
                ),
                url=c.get("url", ""),
            ))
        return cards

    async def aclose(self) -> None:
        await self._http.aclose()
