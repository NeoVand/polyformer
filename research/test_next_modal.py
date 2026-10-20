"""No network: budget, identity and restart safeguards for NEXT's paid runner."""
import json
import pathlib
import tempfile
import unittest
from unittest import mock

import next_modal as runner


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.patch = mock.patch.multiple(runner, LEDGER=self.root / 'ledger.json',
                                         LOCK=self.root / 'ledger.lock')
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def job(self, **changes):
        return runner.normalize_job({'script': 'dilution.py', 'argv': ['--seed', '0'],
                                     **changes}, {'dilution.py': 'abc'})

    def test_caps_and_rates(self):
        self.assertEqual(runner.CAPS, {'experiment1': 15., 'experiment2': 20.})
        self.assertEqual(runner.TOTAL_CAP, 35.)
        self.assertGreater(runner.rate('L4'), .000222)

    def test_repeated_reservation_does_not_duplicate(self):
        j = self.job()
        spec = {'name': 'pilot', 'stage': 'experiment1', 'sha256': 'x'}
        _, fresh = runner.reserve(spec, j)
        self.assertTrue(fresh)
        _, fresh = runner.reserve(spec, j)
        self.assertFalse(fresh)
        with runner.locked_ledger() as ledger:
            self.assertEqual(len(ledger['jobs']), 1)
            self.assertEqual(runner.totals(ledger)['total'], j['reserved_usd'])

    def test_unresolved_jobs_retain_full_reservations(self):
        spec = {'name': 'pilot', 'stage': 'experiment1', 'sha256': 'x'}
        j = self.job()
        j['reserved_usd'] = 14.9
        runner.reserve(spec, j)
        with self.assertRaisesRegex(RuntimeError, 'budget reservation refused'):
            runner.reserve(spec, self.job(attempt=1))

    def test_time_limit_not_silent_retry(self):
        self.assertEqual(self.job()['id'], self.job(max_seconds=1200)['id'])
        self.assertNotEqual(self.job()['id'], self.job(attempt=1)['id'])

    def test_bad_specs(self):
        for kwargs in ({'max_seconds': 0}, {'gpu': 'unknown'}, {'argv': '--seed 0'},
                       {'script': '../dilution.py'}, {'attempt': -1}):
            with self.assertRaises(ValueError):
                self.job(**kwargs)


if __name__ == '__main__':
    unittest.main()
