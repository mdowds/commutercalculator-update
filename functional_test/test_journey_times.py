import datetime
from unittest import TestCase

import updaters
from functional_test.mockfirestore import MockFirestore
from functional_test.mockfirestore.main import GeoPoint
from interfaces.database import Database
from updaters import JourneyTimesInteractor

lbg = {
    'sid': 'LBG',
    'name': 'London Bridge',
    'location': GeoPoint(0.0, 0.0)
}
kgx = {
    'sid': 'KGX',
    'name': 'Kings Cross',
    'location': GeoPoint(0.0, 0.0)
}


class JourneyTimesTests(TestCase):

    def setUp(self):
        self.mock_db = MockFirestore()
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)

        db = Database(self.mock_db)
        self.interactor = JourneyTimesInteractor(db, debug=True)

    def test_updatesJourneyTimes(self):
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

        expected = {
            'origin': {
                'sid': 'KGX',
                'location': GeoPoint(latitude=0.0, longitude=0.0),
                'name': 'Kings Cross'
            },
            'time': 10
        }
        self.assertEqual(expected, journey)

    def test_updatesTheLeastRecentlyUpdated(self):
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

    def test_updatesOneDestinationPerRun(self):
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

    def test_updatesTimestampAfterRun(self):
        original_update_time = datetime.datetime(2018, 12, 1)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_times_updated': original_update_time
        })

        updaters.update(self.interactor)

        new_update_time = self.mock_db.collection('destinations').document('LBG')\
            .get().to_dict()['journey_times_updated']

        self.assertGreater(new_update_time, original_update_time)
