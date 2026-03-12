import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.infrastructure.waha.client import WAHAClient
from app.interfaces.http.health import router as health_router
from app.interfaces.http.notify import router as notify_router
from scheduler.jobs import setup_scheduler, scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────
    logger.info("=== Project Guardian starting up ===")

    waha = WAHAClient()
    app.state.waha = waha

    # Register cron jobs and start scheduler
    setup_scheduler(waha_client=waha, settings=get_settings())
    scheduler.start()
    logger.info("Scheduler started.")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────
    logger.info("=== Project Guardian shutting down ===")
    scheduler.shutdown(wait=False)
    await waha.aclose()


app = FastAPI(
    title="Project Guardian",
    description="Proactive headless agent — WhatsApp task notifications for dev teams.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health_router, prefix="/api/v1")
app.include_router(notify_router, prefix="/api/v1")
