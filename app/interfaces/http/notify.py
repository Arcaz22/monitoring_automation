from datetime import datetime

from fastapi import APIRouter, Request

from app.application.usecases.guardian import GuardianUseCase
from app.infrastructure.trello.client import TrelloClient
from app.presentation.schemas.notify import (
    SendTestRequest, SendTestResponse,
    TrelloNotifyRequest, TrelloNotifyResponse, NotificationResult,
    WahaMessageDTO,
)

router = APIRouter(tags=["Notify"])


@router.post(
    "/notify/test",
    response_model=SendTestResponse,
    summary="Step 1 — Send hello testing via WAHA",
)
async def notify_test(body: SendTestRequest, request: Request) -> SendTestResponse:
    usecase = GuardianUseCase(waha=request.app.state.waha)
    result = await usecase.send_hello(phone=body.phone)
    return SendTestResponse(
        status="sent",
        phone=body.phone or "default (TEST_PHONE in .env)",
        waha_response=WahaMessageDTO(
            chat_id=result.chat_id,
            text=result.text,
            sent_at=result.sent_at,
            status=result.status,
        ),
    )


@router.post(
    "/notify/trello",
    response_model=TrelloNotifyResponse,
    summary="Manual trigger — run Guardian Trello check now",
)
async def notify_trello(body: TrelloNotifyRequest, request: Request) -> TrelloNotifyResponse:
    trello = TrelloClient()
    try:
        usecase = GuardianUseCase(
            waha=request.app.state.waha,
            trello=trello,
        )
        run_result = await usecase.run(
            dry_run=body.dry_run,
            board_id=body.board_id,
        )
    finally:
        await trello.aclose()

    return TrelloNotifyResponse(
        status="ok",
        dry_run=run_result.dry_run,
        total_cards=run_result.total_cards,
        total_sent=run_result.total_sent,
        total_failed=run_result.total_failed,
        results=[
            NotificationResult(
                recipient_name=r.recipient_name,
                recipient_wa=r.recipient_wa,
                card_name=r.card_name,
                type=r.type,
                sent=r.sent,
                error=r.error,
            )
            for r in run_result.results
        ],
        triggered_at=run_result.triggered_at,
    )
