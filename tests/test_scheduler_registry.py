import unittest

from apscheduler.triggers.cron import CronTrigger

from src.config import settings
from src.scheduler.cli import main as cli_main
from src.scheduler.registry import JOBS, cron_trigger_for, get_job


class SchedulerRegistryTests(unittest.TestCase):
    def test_all_jobs_have_parseable_cron(self) -> None:
        for job in JOBS:
            trigger = cron_trigger_for(job)
            self.assertIsInstance(trigger, CronTrigger)

    def test_default_cron_expressions(self) -> None:
        by_id = {job.id: job.cron for job in JOBS}
        self.assertEqual(by_id["job_popular_assets"], settings.CRON_POPULAR_ASSETS)
        self.assertEqual(by_id["job_fear_and_greed"], settings.CRON_FEAR_AND_GREED)
        self.assertEqual(settings.CRON_POPULAR_ASSETS, "0 */4 * * *")
        self.assertEqual(settings.CRON_FEAR_AND_GREED, "0 0,12 * * *")

    def test_get_job_known_and_unknown(self) -> None:
        self.assertIsNotNone(get_job("job_popular_assets"))
        self.assertIsNone(get_job("no_such_job"))

    def test_cli_list_exits_zero(self) -> None:
        self.assertEqual(cli_main(["list"]), 0)

    def test_cli_run_unknown_job_exits_nonzero(self) -> None:
        self.assertEqual(cli_main(["run", "unknown_job_id"]), 1)


if __name__ == "__main__":
    unittest.main()