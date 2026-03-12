import logging
from typing import Callable, Awaitable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.settings import Settings
from app.infrastructure.waha.client import WAHAClient
from app.application.usecases.guardian import GuardianUseCase

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")


def _make_guardian_hello_job(
    waha_client: WAHAClient,
) -> Callable[[], Awaitable[None]]:
    async def _run() -> None:
        logger.info("[Scheduler] Cron fired — running GuardianUseCase.send_hello()")
        try:
            usecase = GuardianUseCase(waha_client)
            result = await usecase.send_hello()
            logger.info("[Scheduler] Job completed → %s", result)
        except Exception as exc:
            logger.error("[Scheduler] Job 'guardian_hello' failed: %s", exc, exc_info=True)

    return _run


def setup_scheduler(
    *,
    waha_client: WAHAClient,
    settings: Settings,
) -> AsyncIOScheduler:
    job_func = _make_guardian_hello_job(waha_client)

    scheduler.add_job(
        func=job_func,
        trigger=CronTrigger(
            hour=settings.scheduler_hour,
            minute=settings.scheduler_minute,
        ),
        id="guardian_hello",
        name="Guardian — Hello Testing",
        replace_existing=True,
        misfire_grace_time=60,
        coalesce=True,
    )

    logger.info(
        "[Scheduler] Job 'guardian_hello' registered → runs daily at %02d:%02d (Asia/Jakarta)",
        settings.scheduler_hour,
        settings.scheduler_minute,
    )

    return scheduler
