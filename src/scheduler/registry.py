from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from apscheduler.triggers.cron import CronTrigger

from src.config import settings
from src.scheduler import tasks

MISFIRE_GRACE_TIME_SECONDS = 300


@dataclass(frozen=True)
class ScheduledJob:
    id: str
    cron: str
    coroutine: Callable[[], Awaitable[None]]


def build_scheduled_jobs() -> tuple[ScheduledJob, ...]:
    return (
        ScheduledJob("job_popular_assets", settings.CRON_POPULAR_ASSETS, tasks.refresh_popular_assets),
        ScheduledJob("job_fear_and_greed", settings.CRON_FEAR_AND_GREED, tasks.refresh_fear_and_greed),
    )


JOBS: tuple[ScheduledJob, ...] = build_scheduled_jobs()


def get_job(job_id: str) -> ScheduledJob | None:
    for job in JOBS:
        if job.id == job_id:
            return job
    return None


def cron_trigger_for(job: ScheduledJob) -> CronTrigger:
    return CronTrigger.from_crontab(job.cron, timezone=settings.TIMEZONE)