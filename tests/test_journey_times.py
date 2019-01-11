import datetime
from urllib.parse import urlparse, parse_qsl
from unittest import TestCase

import responses

import updaters
from tests.helpers import make_station_dict
from tests.mockfirestore import MockFirestore
from tests.mockfirestore import GeoPoint
from interfaces.database import Database
from updaters import JourneyTimesInteractor

lbg = make_station_dict('LBG', 'London Bridge', location=GeoPoint(1.0, 1.0))
kgx = make_station_dict('KGX', 'Kings Cross', location=GeoPoint(0.0, 0.0))


class JourneyTimesTests(TestCase):

    def setUp(self):
        self.mock_db = MockFirestore()
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)

        db = Database(self.mock_db)
        self.interactor = JourneyTimesInteractor(db, api_key='key0', debug=True)

    @responses.activate
    def test_updatesJourneyTimes(self):

        self._stub_directions_response(10)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg, 'journey_times_updated': 0
        })

        update_results = updaters.update(self.interactor)

        self.assertFalse(update_results.has_errors)

        journey = self.mock_db \
            .collection('destinations') \
            .document('LBG') \
            .collection('journeys') \
            .document('KGX') \
            .get().to_dict()

        self.assertEqual(10, journey['time'])
        self.assertEqual(kgx, journey['origin'])
        self.assertRequestParamsCorrect(origin=kgx, destination=lbg)

    @responses.activate
    def test_updatesTheLeastRecentlyUpdated(self):
        self._stub_directions_response(10)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_times_updated': datetime.datetime(2018, 12, 2)
        })
        self.mock_db.collection('destinations').document('KGX').set({
            **kgx,
            'journey_times_updated': datetime.datetime(2018, 12, 1)
        })

        updaters.update(self.interactor)

        journeys_to_kgx = self.mock_db \
            .collection('destinations') \
            .document('KGX') \
            .collection('journeys') \
            .get()

        self.assertEqual(1, len(journeys_to_kgx))
        self.assertRequestParamsCorrect(origin=lbg, destination=kgx)

    @responses.activate
    def test_updatesOneDestinationPerRun(self):
        self._stub_directions_response(10)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_times_updated': datetime.datetime(2018, 12, 1)
        })
        self.mock_db.collection('destinations').document('KGX').set({
            **kgx,
            'journey_times_updated': datetime.datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journeys_to_lbg = self.mock_db \
            .collection('destinations') \
            .document('LBG') \
            .collection('journeys') \
            .get()

        journeys_to_kgx = self.mock_db \
            .collection('destinations') \
            .document('KGX') \
            .collection('journeys') \
            .get()

        self.assertEqual(1, len(journeys_to_lbg))
        self.assertEqual(0, len(journeys_to_kgx))

    @responses.activate
    def test_updatesTimestampAfterRun(self):
        self._stub_directions_response(10)
        original_update_time = datetime.datetime(2018, 12, 1)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_times_updated': original_update_time
        })

        updaters.update(self.interactor)

        new_update_time = self.mock_db.collection('destinations').document('LBG')\
            .get().to_dict()['journey_times_updated']

        self.assertGreater(new_update_time, original_update_time)

    def _stub_directions_response(self, journey_time: int):
        stub_response = {'routes': [{
            'legs': [{
                'duration': {
                    'value': journey_time * 60
                }
            }]
        }]}

        responses.add(responses.GET, 'https://maps.googleapis.com/maps/api/directions/json', json=stub_response)

    def assertRequestParamsCorrect(self, origin, destination):
        request_url = urlparse(responses.calls[0].request.url)
        request_params = dict(parse_qsl(request_url.query))

        origin_coords = '%s,%s' % (origin['location'].latitude, origin['location'].longitude)
        dest_coords = '%s,%s' % (destination['location'].latitude, destination['location'].longitude)

        self.assertEqual(origin_coords, request_params['origin'])
        self.assertEqual(dest_coords, request_params['destination'])
        self.assertEqual('transit', request_params['mode'])
        self.assertEqual('key0', request_params['key'])
        self.assertIsNotNone(request_params['arrival_time'])
