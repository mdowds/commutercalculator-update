from unittest import TestCase
from datetime import datetime

from playhouse.test_utils import test_database
from peewee import SqliteDatabase
from fn import _
from fnplus import tfilter

from update_journey_times import *

test_db = SqliteDatabase(':memory:')


class TestUpdateJourneyTimes(TestCase):
    def run(self, result=None):
        # All queries will be run in `test_db`
        with test_database(test_db, [Station]):
            super(TestUpdateJourneyTimes, self).run(result)

    def test_get_stations_returns_correct_limit(self):
        self.assertEqual(3, len(self._run_get_stations()))

    def test_get_stations_orders_by_last_updated(self):
        self.assertEqual('BAR', self._run_get_stations()[0].sid)

    def test_get_stations_limits_to_zone1(self):
        self.assertEqual(0, len(tfilter(lambda s: s.min_zone != 1 and s.max_zone != 1, self._run_get_stations())))

    # Helpers

    def _run_get_stations(self):
        stations = get_stations(Station)
        if len(stations) > 0:
            return stations
        else:
            self._create_test_data()
            return get_stations(Station)

    def _create_test_data(self):
        Station.create(sid='FOO', min_zone=1, max_zone=1, journey_times_updated=self._make_datetime('10'))
        Station.create(sid='BAR', min_zone=1, max_zone=1, journey_times_updated=self._make_datetime('05'))
        Station.create(sid='BAZ', min_zone=1, max_zone=2, journey_times_updated=self._make_datetime('12'))
        Station.create(sid='FOZ', min_zone=2, max_zone=2, journey_times_updated=self._make_datetime('09'))

    @staticmethod
    def _make_datetime(day):
        return datetime.strptime(day + ' 06 2016', '%d %m %Y')