from unittest import TestCase

from models import JourneyTime
from updaters.updater import *
from updaters.updater import _update_journey, _update_destinations, _update_destination
from tests.helpers import create_station_test_data


class TestUpdater(TestCase):

    def setUp(self):
        self._all_stations = create_station_test_data()
        self._interactor = MockUpdaterInteractor(self._all_stations)

    def test_update(self):
        result = update(self._interactor)

        self.assertEqual("3 stations updated with 9 records created and 0 errors", result.message)
        self.assertFalse(result.has_errors)

    def test_update_with_error(self):
        self._interactor.return_error = True
        result = update(self._interactor)

        self.assertEqual("3 stations updated with 0 records created and 9 errors", result.message)
        self.assertTrue(result.has_errors)

    def test_update_destinations(self):
        updated = _update_destinations(self._interactor)
        self.assertEqual((3,9,0), updated)

    def test_update_destination(self):
        destination = self._all_stations[0]
        updated = _update_destination(self._interactor, destination)
        self.assertEqual((3,0), updated)
        self.assertTrue(self._interactor.update_dest_record_called)

    def test_update_destination_error(self):
        destination = self._all_stations[0]
        self._interactor.return_error = True
        updated = _update_destination(self._interactor, destination)
        self.assertEqual((0,3), updated)
        self.assertFalse(self._interactor.update_dest_record_called)

    def test_update_journey(self):
        origin = self._all_stations[0]
        dest = self._all_stations[1]
        result = _update_journey(self._interactor, dest, origin).value

        self.assertEqual(result.origin, origin)
        self.assertEqual(result.destination, dest)
        self.assertEqual(result.time, 12)

    def test_update_journey_with_error(self):
        origin = self._all_stations[0]
        dest = self._all_stations[1]
        self._interactor.return_error = True
        result = _update_journey(self._interactor, dest, origin).error

        self.assertEqual(result.__str__(), "Error")


class MockUpdaterInteractor(UpdaterInteractor):
    def __init__(self, all_stations):
        super().__init__(False)
        self._all_stations = all_stations
        self.return_error = False
        self.update_dest_record_called = False

    def get_stations_to_update(self) -> Tuple[Station, ...]:
        return self._all_stations[0:3]

    def get_all_stations(self) -> Tuple[Station, ...]:
        return self._all_stations

    def update_dest_record(self, destination: Station, time: datetime):
        self.update_dest_record_called = True

    def get_update(self, destination: Station, origin: Station) -> Either:
        if self.return_error: return Either(None, Exception("Error"))
        return Either(12)

    @curried
    def save_update(self, destination: Station, origin: Station, value):
        return JourneyTime(origin=origin, destination=destination, time=value)
