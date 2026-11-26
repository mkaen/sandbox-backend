import asyncio
import signal

from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_JOB_SUBMITTED,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import settings
from src.core.logger import configure_logging, logger
from src.scheduler.registry import (
    MISFIRE_GRACE_TIME_SECONDS,
    JOBS,
    cron_trigger_for,
)


def _log_scheduler_event(event) -> None:
    job_id = getattr(event, "job_id", None)
    if event.code == EVENT_JOB_SUBMITTED:
        logger.info("Scheduler job submitted (will run): %s", job_id)
    elif event.code == EVENT_JOB_EXECUTED:
        logger.info("Scheduler job completed: %s", job_id)
    elif event.code == EVENT_JOB_MISSED:
        logger.warning("Scheduler job missed run: %s", job_id)
    elif event.code == EVENT_JOB_ERROR:
        exc = getattr(event, "exception", None)
        if exc is not None:
            logger.error(
                "Scheduler job failed: %s — %s",
                job_id,
                exc,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
        else:
            logger.error("Scheduler job failed: %s", job_id)


def _register_jobs(scheduler: AsyncIOScheduler) -> None:
    for job in JOBS:
        scheduler.add_job(
            job.coroutine,
            cron_trigger_for(job),
            id=job.id,
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=MISFIRE_GRACE_TIME_SECONDS,
        )
        logger.info("Registered scheduler job %s with cron %s", job.id, job.cron)


async def run_scheduler() -> None:
    if not settings.SCHEDULER_ENABLED:
        logger.warning("SCHEDULER_ENABLED is false; exiting without starting jobs")
        return

    scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
    scheduler.add_listener(
        _log_scheduler_event,
        EVENT_JOB_SUBMITTED | EVENT_JOB_EXECUTED | EVENT_JOB_MISSED | EVENT_JOB_ERROR,
    )
    _register_jobs(scheduler)
    scheduler.start()
    logger.info("Scheduler started (timezone=%s)", settings.TIMEZONE)

    stop = asyncio.Event()

    def request_shutdown() -> None:
        stop.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, request_shutdown)

    try:
        await stop.wait()
    finally:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def main() -> None:
    configure_logging()
    asyncio.run(run_scheduler())


if __name__ == "__main__":
    main()