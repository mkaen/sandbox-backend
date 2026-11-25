import asyncio
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import settings
from src.core.logger import configure_logging, logger
from src.scheduler.registry import (
    MISFIRE_GRACE_TIME_SECONDS,
    JOBS,
    cron_trigger_for,
)


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