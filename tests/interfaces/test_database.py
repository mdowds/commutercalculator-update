from unittest import TestCase

from playhouse.test_utils import test_database
from peewee import SqliteDatabase
from fnplus import tfilter

from interfaces.database import *
from models import SeasonTicket
from tests import helpers


class TestUpdateJourneyTimes(TestCase):

    test_db = SqliteDatabase(':memory:')

    def setUp(self):
        self._all_stations = self.setUp_station_data()
        self._season_tickets = self.setUp_season_ticket_data()
        self._fooStation = self._all_stations[0]
        self._barStation = self._all_stations[1]

    def tearDown(self):
        Station.delete()
        SeasonTicket.delete()

    def run(self, result=None):
        # All queries will be run in `test_db`
        with test_database(self.test_db, [Station, JourneyTime, SeasonTicket]):
            super(TestUpdateJourneyTimes, self).run(result)

    def test_get_stations_for_journey_time_update_returns_correct_limit(self):
        self.assertEqual(3, len(get_stations_for_journey_time_update()))

    def test_get_stations_for_journey_time_update_orders_by_last_updated(self):
        self.assertEqual('BAR', get_stations_for_journey_time_update()[0].sid)

    def test_get_stations_for_journey_time_update_limits_to_zone1(self):
        self.assertEqual(0,
                         len(tfilter(
                             lambda s: s.min_zone != 1 and s.max_zone != 1,
                             get_stations_for_journey_time_update())
                         ))

    def test_get_all_stations_returns_all(self):
        self.assertEqual(4, len(get_all_stations()))

    def test_get_all_stations_orders_by_name(self):
        self.assertEqual('Bar', get_all_stations()[0].name)

    def test_save_journey_time(self):
        res = save_journey_time(self._fooStation, self._barStation, 10)
        self.assertEqual(10, res.time)

    def test_update_journey_times_updated(self):
        date = helpers.make_datetime('01')
        res = update_journey_times_updated(self._fooStation, date)
        self.assertEqual(date, res.journey_times_updated)

    def test_get_station_for_season_ticket_update_returns_correct_station(self):
        res = get_station_for_season_ticket_update()
        self.assertEqual('NR', res.modes)
        self.assertEqual(0, len(SeasonTicket.select().where(SeasonTicket.destination == res)))

    def test_get_all_nr_stations_returns_correct_results(self):
        self.assertEqual(3, len(get_all_nr_stations()))

    # Helpers

    def setUp_station_data(self) -> Tuple[Station, ...]:
        stations = helpers.create_station_test_data()
        for station in stations: station.save(force_insert=True)
        return stations

    def setUp_season_ticket_data(self) -> Tuple[SeasonTicket, ...]:
        season_tickets = helpers.create_season_ticket_test_data()
        for season_ticket in season_tickets: season_ticket.save(force_insert=True)
        return season_tickets
