import argparse
import asyncio
import sys

from src.core.logger import configure_logging, logger
from src.scheduler.registry import JOBS, get_job


def _cmd_list() -> int:
    for job in JOBS:
        print(f"{job.id}\t{job.cron}")
    return 0


async def _cmd_run(job_id: str) -> int:
    job = get_job(job_id)
    if job is None:
        logger.error("Unknown job id: %s", job_id)
        return 1
    await job.coroutine()
    return 0


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Run scheduled jobs manually")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List job ids and cron expressions")

    run_parser = sub.add_parser("run", help="Run a single job once")
    run_parser.add_argument("job_id", help="Job id (see: list)")

    args = parser.parse_args(argv)
    if args.command == "list":
        return _cmd_list()
    if args.command == "run":
        return asyncio.run(_cmd_run(args.job_id))
    return 1


if __name__ == "__main__":
    sys.exit(main())