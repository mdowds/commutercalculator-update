from unittest import TestCase

from peewee import SqliteDatabase

from update_journey_times import *
from tests.helpers import make_datetime

test_db = SqliteDatabase(':memory:')


class TestUpdateJourneyTimes(TestCase):

    def test_update_destinations(self):
        all_stations = self._create_test_data()
        destinations = self._create_test_data()[0:3]
        updated = update_destinations(all_stations, destinations)
        self.assertEqual(('Foo', 'Bar', 'Baz'), updated)

    def test_update_destination(self):
        all_stations = self._create_test_data()
        destination = self._create_test_data()[0]
        updated = update_destination(all_stations, destination)
        self.assertEqual('Foo', updated)

    # Helpers

    def _create_test_data(self):
        return (
            Station(sid='FOO', name='Foo', min_zone=1, max_zone=1, journey_times_updated=make_datetime('10')),
            Station(sid='BAR', name='Bar', min_zone=1, max_zone=1, journey_times_updated=make_datetime('05')),
            Station(sid='BAZ', name='Baz', min_zone=1, max_zone=2, journey_times_updated=make_datetime('12')),
            Station(sid='FOZ', name='Foz', min_zone=2, max_zone=2, journey_times_updated=make_datetime('09'))
        )
