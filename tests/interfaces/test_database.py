from unittest import TestCase

from playhouse.test_utils import test_database
from peewee import SqliteDatabase
from fnplus import tfilter

from interfaces.database import *
from tests.helpers import make_datetime

test_db = SqliteDatabase(':memory:')


class TestUpdateJourneyTimes(TestCase):

    _fooStation = Station(sid='FOO', name='Foo', min_zone=1, max_zone=1, journey_times_updated=make_datetime('10'))
    _barStation = Station(sid='BAR', name='Bar', min_zone=1, max_zone=1, journey_times_updated=make_datetime('05'))

    def run(self, result=None):
        # All queries will be run in `test_db`
        with test_database(test_db, [Station, JourneyTime]):
            super(TestUpdateJourneyTimes, self).run(result)

    def test_get_stations_to_update_returns_correct_limit(self):
        self.assertEqual(3, len(self._run_get_stations_to_update()))

    def test_get_stations_to_update_orders_by_last_updated(self):
        self.assertEqual('BAR', self._run_get_stations_to_update()[0].sid)

    def test_get_stations_to_update_limits_to_zone1(self):
        self.assertEqual(0, len(tfilter(lambda s: s.min_zone != 1 and s.max_zone != 1, self._run_get_stations_to_update())))

    def test_get_all_stations_returns_all(self):
        self.assertEqual(4, len(self._run_get_all_stations()))

    def test_get_all_stations_orders_by_name(self):
        self.assertEqual('Bar', self._run_get_all_stations()[0].name)

    def test_save_journey_time(self):
        res = save_journey_time(self._fooStation, self._barStation, 10)
        self.assertEqual(10, res.time)

    # Helpers

    def _run_get_stations_to_update(self):
        return self._run_station_query_func(get_stations_to_update)

    def _run_get_all_stations(self):
        return self._run_station_query_func(get_all_stations)

    def _run_station_query_func(self, f):
        stations = f(Station)
        if len(stations) > 0:
            return stations
        else:
            self._save_test_data()
            return f(Station)

    def _save_test_data(self):
        for station in self._create_test_data(): station.save(force_insert=True)

    def _create_test_data(self):
        return (
            self._fooStation,
            self._barStation,
            Station(sid='BAZ', name='Baz', min_zone=1, max_zone=2, journey_times_updated=make_datetime('12')),
            Station(sid='FOZ', name='Foz', min_zone=2, max_zone=2, journey_times_updated=make_datetime('09'))
        )
