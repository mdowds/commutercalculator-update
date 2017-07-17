from unittest import TestCase

from updaters.journey_times import *
from updaters.journey_times import _update_journey, _update_destinations, _update_destination, _output_message
from tests.helpers import create_test_data


class TestUpdateJourneyTimes(TestCase):

    def setUp(self):
        self._all_stations = create_test_data()

    def test_update_destinations(self):
        destinations = self._all_stations[0:3]
        updated = _update_destinations(self._mock_get_time, self._mock_save_journey, self._mock_update_dest_record, self._all_stations, destinations)
        self.assertEqual((3,9,0), updated)

    def test_update_destination(self):
        destination = self._all_stations[0]
        updated = _update_destination(self._mock_get_time, self._mock_save_journey, self._mock_update_dest_record, self._all_stations, destination)
        self.assertEqual((3,0), updated)

    def test_update_destination_error(self):
        destination = self._all_stations[0]
        updated = _update_destination(self._mock_get_time_error, self._mock_save_journey, self._mock_update_dest_record, self._all_stations, destination)
        self.assertEqual((0,3), updated)

    def test_update_journey(self):
        origin = self._all_stations[0]
        dest = self._all_stations[1]
        result = _update_journey(self._mock_get_time, self._mock_save_journey, dest, origin).get_value()

        self.assertEqual(result.origin, origin)
        self.assertEqual(result.destination, dest)
        self.assertEqual(result.time, self._mock_get_time().get_value())

    def test_update_journey_with_error(self):
        origin = self._all_stations[0]
        dest = self._all_stations[1]
        result = _update_journey(self._mock_get_time_error, self._mock_save_journey, dest, origin).get_error()

        self.assertEqual(result.__str__(), self._mock_get_time_error().get_error().__str__())

    def test_output_message(self):
        self.assertEqual("2 stations updated with 3 journey records created and 0 errors", _output_message((2,3,0)))

    # Helpers

    # def _create_test_data(self):
    #     return (
    #         Station(sid='FOO', name='Foo', min_zone=1, max_zone=1, journey_times_updated=make_datetime('10')),
    #         Station(sid='BAR', name='Bar', min_zone=1, max_zone=1, journey_times_updated=make_datetime('05')),
    #         Station(sid='BAZ', name='Baz', min_zone=1, max_zone=2, journey_times_updated=make_datetime('12')),
    #         Station(sid='FOZ', name='Foz', min_zone=2, max_zone=2, journey_times_updated=make_datetime('09'))
    #     )

    @staticmethod
    def _mock_get_time(d:Station=None, o:Station=None):
        return Either(12)

    @staticmethod
    def _mock_get_time_error(d:Station=None, o:Station=None):
        return Either(None, Exception("Error"))

    @staticmethod
    @curried
    def _mock_save_journey(d: Station, o: Station, t: int):
        return JourneyTime(origin=o, destination=d, time=t)

    @staticmethod
    def _mock_update_dest_record(s: Station, t: datetime):
        s.journey_times_updated = t
        return s
