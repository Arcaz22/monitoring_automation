import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.infrastructure.trello.client import TrelloClient
from app.application.usecases.guardian import GuardianUseCase

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")


def _make_job(waha_client, settings):
    async def _run():
        logger.info("[Scheduler] Cron fired — running Guardian full check")
        trello  = TrelloClient()
        usecase = GuardianUseCase(waha=waha_client, trello=trello)
        try:
            result = await usecase.run(dry_run=False)
            logger.info(
                "[Scheduler] Done — cards: %d, sent: %d, failed: %d",
                result.total_cards, result.total_sent, result.total_failed,
            )
        except Exception as e:
            logger.error("[Scheduler] Job failed: %s", e, exc_info=True)
        finally:
            await trello.aclose()

    return _run


def setup_scheduler(waha_client, settings) -> AsyncIOScheduler:
    job = _make_job(waha_client, settings)

    scheduler.add_job(
        job,
        trigger=CronTrigger(
            hour=settings.scheduler_hour,
            minute=settings.scheduler_minute,
        ),
        id="guardian_daily",
        name="Guardian — Daily Trello Check",
        replace_existing=True,
        misfire_grace_time=60,
    )

    logger.info(
        "[Scheduler] Job registered → runs daily at %02d:%02d (Asia/Jakarta)",
        settings.scheduler_hour,
        settings.scheduler_minute,
    )
    return scheduler
