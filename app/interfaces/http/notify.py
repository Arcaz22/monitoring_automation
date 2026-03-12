from fastapi import APIRouter, Request

from app.application.usecases.guardian import GuardianUseCase
from app.presentation.schemas.notify import SendRequest, NotifyResponse

router = APIRouter(tags=["Notify"])


@router.post(
    "/notify/test",
    response_model=NotifyResponse,
    summary="Manual trigger — sends 'hello testing' via WAHA",
)
async def notify_test(body: SendRequest, request: Request) -> NotifyResponse:
    waha    = request.app.state.waha
    usecase = GuardianUseCase(waha)
    result  = await usecase.send_hello(phone=body.phone)

    return NotifyResponse(
        status="sent",
        phone=body.phone or "default (see TEST_PHONE in .env)",
        waha_response=result,
    )
