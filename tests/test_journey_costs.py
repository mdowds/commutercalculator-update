import datetime
from unittest import TestCase

import responses

import updaters
from tests import helpers
from tests.mockfirestore import MockFirestore
from interfaces.database import Database
from updaters.journey_costs_interactor import JourneyCostsInteractor

lbg = helpers.make_station_dict('LBG', 'London Bridge', zones=[1])
kgx = helpers.make_station_dict('KGX', 'Kings Cross', zones=[1])
vxh = helpers.make_station_dict('VXH', 'Vauxhall', zones=[1, 2])
sra = helpers.make_station_dict('SRA', 'Stratford', zones=[2, 3])


class JourneyCostsTests(TestCase):

    def setUp(self):
        self.mock_db = MockFirestore()

        db = Database(self.mock_db)
        self.interactor = JourneyCostsInteractor(db, debug=True)

    def test_updatesTravelcardPrices(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journeys': helpers.make_journey_dict(kgx),
            'journey_costs_updated': datetime.datetime(2018, 12, 2)
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
            'min_zone': 1,
            'max_zone': 1,
            'annual_price': 1404
        }
        self.assertEqual(expected, journey['travelcard'])

    def test_updatesTravelcardPrices_forMultiZoneStations(self):
        self.mock_db.collection('stations').document('VXH').set(vxh)
        self.mock_db.collection('stations').document('SRA').set(sra)
        self.mock_db.collection('destinations').document('VXH').set({
            **vxh,
            'journeys': helpers.make_journey_dict(sra),
            'journey_costs_updated': datetime.datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('VXH') \
            .collection('journeys') \
            .document('SRA') \
            .get().to_dict()

        expected = {
            'min_zone': 2,
            'max_zone': 2,
            'annual_price': 1052
        }
        self.assertEqual(expected, journey['travelcard'])

    def test_updatesTravelcardPrices_forMultiZoneStations_bothInZone1(self):
        self.mock_db.collection('stations').document('VXH').set(vxh)
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('destinations').document('VXH').set({
            **vxh,
            'journeys': helpers.make_journey_dict(lbg),
            'journey_costs_updated': datetime.datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('VXH') \
            .collection('journeys') \
            .document('LBG') \
            .get().to_dict()

        expected = {
            'min_zone': 1,
            'max_zone': 1,
            'annual_price': 1404
        }
        self.assertEqual(expected, journey['travelcard'])

    def test_createsJourneyEntry_ifItDoesNotExist(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_costs_updated': datetime.datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('LBG') \
            .collection('journeys') \
            .document('KGX') \
            .get().to_dict()

        expected = {
            'min_zone': 1,
            'max_zone': 1,
            'annual_price': 1404
        }
        self.assertEqual(expected, journey['travelcard'])

    def test_updatesTheLeastRecentlyUpdated(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)

        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_costs_updated': datetime.datetime(2018, 12, 2)
        })
        self.mock_db.collection('destinations').document('KGX').set({
            **kgx,
            'journey_costs_updated': datetime.datetime(2018, 12, 1)
        })

        updaters.update(self.interactor)

        journeys_to_kgx = self.mock_db \
            .collection('destinations') \
            .document('KGX') \
            .collection('journeys') \
            .get()

        self.assertEqual(1, len(journeys_to_kgx))

    # TODO make this pass
    # def test_doesNotUpdateDestinationsUpdatedThisYear(self):
    #     self.mock_db.collection('stations').document('LBG').set(lbg)
    #     self.mock_db.collection('stations').document('KGX').set(kgx)
    #
    #     this_year = datetime.date.today().year
    #     self.mock_db.collection('destinations').document('LBG').set({
    #         **lbg,
    #         'journey_costs_updated': datetime.datetime(this_year, 12, 2)
    #     })
    #
    #     updaters.update(self.interactor)
    #
    #     journey = self.mock_db \
    #         .collection('destinations') \
    #         .document('LBG') \
    #         .collection('journeys') \
    #         .document('KGX') \
    #         .get().to_dict()
    #
    #     self.assertTrue('travelcard' not in journey)

    def test_updatesOneDestinationPerRun(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)

        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_costs_updated': datetime.datetime(2018, 12, 1)
        })
        self.mock_db.collection('destinations').document('KGX').set({
            **kgx,
            'journey_costs_updated': datetime.datetime(2018, 12, 2)
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
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)

        original_update_time = datetime.datetime(2018, 12, 1)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_costs_updated': original_update_time
        })

        updaters.update(self.interactor)

        new_update_time = self.mock_db.collection('destinations').document('LBG')\
            .get().to_dict()['journey_costs_updated']

        self.assertGreater(new_update_time, original_update_time)
