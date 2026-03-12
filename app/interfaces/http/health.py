from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Health check — includes WAHA status")
async def health(request: Request) -> JSONResponse:
    waha        = request.app.state.waha
    waha_alive  = await waha.health_check()
    waha_status = await waha.session_status()

    return JSONResponse({
        "status":       "ok",
        "waha_alive":   waha_alive,
        "waha_session": waha_status,
    })
