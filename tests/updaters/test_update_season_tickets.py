from unittest import TestCase

from updaters.season_tickets import *
from updaters.season_tickets import _update_destination, _update_season_ticket, _output_message
from tests import helpers


class TestUpdateJourneyTimes(TestCase):

    def setUp(self):
        self._all_stations = tuple(station for station in helpers.create_station_test_data() if station.modes == 'NR')

    def test_update_destination(self):
        destination = self._all_stations[0]
        updated = _update_destination(self._mock_get_price, self._mock_save_season_ticket, self._all_stations, destination)
        self.assertEqual((2,0), updated)

    def test_update_destination_error(self):
        destination = self._all_stations[0]
        updated = _update_destination(self._mock_get_price_error, self._mock_save_season_ticket, self._all_stations, destination)
        self.assertEqual((0,2), updated)

    def test_update_journey(self):
        origin = self._all_stations[0]
        dest = self._all_stations[1]
        result = _update_season_ticket(self._mock_get_price, self._mock_save_season_ticket, dest, origin).value()

        self.assertEqual(result.origin, origin)
        self.assertEqual(result.destination, dest)
        self.assertEqual(result.annual_price, self._mock_get_price().value())

    def test_update_journey_with_error(self):
        origin = self._all_stations[0]
        dest = self._all_stations[1]
        result = _update_season_ticket(self._mock_get_price_error, self._mock_save_season_ticket, dest, origin).error()

        self.assertEqual(result.__str__(), self._mock_get_price_error().error().__str__())

    def test_output_message(self):
        self.assertEqual("1 station updated with 3 season ticket records created and 0 errors", _output_message((1,3,0)))

    # Helpers

    @staticmethod
    def _mock_get_price(d:Station=None, o:Station=None):
        return Either(1000)

    @staticmethod
    def _mock_get_price_error(d:Station=None, o:Station=None) -> Either[int]:
        return Either(None, Exception("Error"))

    @staticmethod
    @curried
    def _mock_save_season_ticket(d: Station, o: Station, p: int):
        return SeasonTicket(origin=o, destination=d, annual_price=p)
