from datetime import datetime, date
from unittest import TestCase

import responses

import updaters
from tests import helpers
from tests.mockfirestore import MockFirestore
from interfaces.database import Database
from updaters.journey_costs_interactor import JourneyCostsInteractor

lbg = helpers.make_station_dict('LBG', 'London Bridge', zones=[1], modes='NR')
kgx = helpers.make_station_dict('KGX', 'Kings Cross', zones=[1], modes='NR')
vxh = helpers.make_station_dict('VXH', 'Vauxhall', zones=[1, 2], modes='NR')
zng = helpers.make_station_dict('ZNG', 'Notting Hill Gate', zones=[1, 2])
sra = helpers.make_station_dict('SRA', 'Stratford', zones=[2, 3], modes='NR')
bah = helpers.make_station_dict('BAH', 'Bank', zones=[1])
snf = helpers.make_station_dict('SNF', 'Shenfield')


class JourneyCostsTests(TestCase):

    def setUp(self):
        self.mock_db = MockFirestore()

        db = Database(self.mock_db)
        self.interactor = JourneyCostsInteractor(db, debug=True)
        self._stub_season_ticket_response(30)

    @responses.activate
    def test_updatesTravelcardPrices(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journeys': helpers.make_journey_dict(kgx),
            'journey_costs_updated': datetime(2018, 12, 2)
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
            'min_zone': '1',
            'max_zone': '1',
            'annual_price': 1404
        }
        self.assertEqual(expected, journey['travelcard'])

    @responses.activate
    def test_updatesSeasonTicketPrices_forNRStations(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('SRA').set(sra)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journeys': helpers.make_journey_dict(sra),
            'journey_costs_updated': datetime(2018, 12, 2)
        })

        update_results = updaters.update(self.interactor)

        self.assertFalse(update_results.has_errors)

        journey = self.mock_db \
            .collection('destinations') \
            .document('LBG') \
            .collection('journeys') \
            .document('SRA') \
            .get().to_dict()

        expected = {
            'annual_price': 1200
        }
        self.assertEqual(expected, journey['season_ticket'])

    @responses.activate
    def test_doesNotUpdateSeasonTicketPrices_forNonNRStations(self):
        responses.add(responses.GET, 'http://api.brfares.com/querysimple', body="Bad Request", status=400)

        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('BAH').set(bah)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journeys': helpers.make_journey_dict(bah),
            'journey_costs_updated': datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('LBG') \
            .collection('journeys') \
            .document('BAH') \
            .get().to_dict()

        self.assertEqual(0, len(responses.calls))
        self.assertTrue('season_ticket' not in journey)

    @responses.activate
    def test_updatesTravelcardPrices_forMultiZoneStations_sameZones(self):
        self.mock_db.collection('stations').document('VXH').set(vxh)
        self.mock_db.collection('stations').document('ZNG').set(zng)
        self.mock_db.collection('destinations').document('VXH').set({
            **vxh,
            'journeys': helpers.make_journey_dict(zng),
            'journey_costs_updated': datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('VXH') \
            .collection('journeys') \
            .document('ZNG') \
            .get().to_dict()

        expected = {
            'min_zone': '2',
            'max_zone': '2',
            'annual_price': 1052
        }
        self.assertEqual(expected, journey['travelcard'])


    @responses.activate
    def test_updatesTravelcardPrices_forMultiZoneStations_differentZones(self):
        self.mock_db.collection('stations').document('VXH').set(vxh)
        self.mock_db.collection('stations').document('SRA').set(sra)
        self.mock_db.collection('destinations').document('VXH').set({
            **vxh,
            'journeys': helpers.make_journey_dict(sra),
            'journey_costs_updated': datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('VXH') \
            .collection('journeys') \
            .document('SRA') \
            .get().to_dict()

        expected = {
            'min_zone': '2',
            'max_zone': '2',
            'annual_price': 1052
        }
        self.assertEqual(expected, journey['travelcard'])

    @responses.activate
    def test_updatesTravelcardPrices_forMultiZoneStations_bothInZone1(self):
        self.mock_db.collection('stations').document('VXH').set(vxh)
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('destinations').document('VXH').set({
            **vxh,
            'journeys': helpers.make_journey_dict(lbg),
            'journey_costs_updated': datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('VXH') \
            .collection('journeys') \
            .document('LBG') \
            .get().to_dict()

        expected = {
            'min_zone': '1',
            'max_zone': '1',
            'annual_price': 1404
        }
        self.assertEqual(expected, journey['travelcard'])

    @responses.activate
    def test_createsJourneyEntry_ifItDoesNotExist(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_costs_updated': datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('LBG') \
            .collection('journeys') \
            .document('KGX') \
            .get().to_dict()

        expected = {
            'min_zone': '1',
            'max_zone': '1',
            'annual_price': 1404
        }
        self.assertEqual(expected, journey['travelcard'])

    @responses.activate
    def test_updatesTheLeastRecentlyUpdated(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)

        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_costs_updated': datetime(2018, 12, 2)
        })
        self.mock_db.collection('destinations').document('KGX').set({
            **kgx,
            'journey_costs_updated': datetime(2018, 12, 1)
        })

        updaters.update(self.interactor)

        journeys_to_kgx = self.mock_db \
            .collection('destinations') \
            .document('KGX') \
            .collection('journeys') \
            .get()

        self.assertEqual(1, len(journeys_to_kgx))

    @responses.activate
    def test_doesNotUpdateDestinationsUpdatedThisYear(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)

        this_year = date.today().year
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_costs_updated': datetime(this_year, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('LBG') \
            .collection('journeys') \
            .document('KGX') \
            .get().to_dict()

        self.assertTrue('travelcard' not in journey)

    @responses.activate
    def test_updatesOneDestinationPerRun(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)

        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_costs_updated': datetime(2018, 12, 1)
        })
        self.mock_db.collection('destinations').document('KGX').set({
            **kgx,
            'journey_costs_updated': datetime(2018, 12, 2)
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
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('KGX').set(kgx)

        original_update_time = datetime(2018, 12, 1)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journey_costs_updated': original_update_time
        })

        updaters.update(self.interactor)

        new_update_time = self.mock_db.collection('destinations').document('LBG')\
            .get().to_dict()['journey_costs_updated']

        self.assertGreater(new_update_time, original_update_time)

    @responses.activate
    def test_updatesTravelcardPrices_forStationsWithSpecialFares(self):
        self.mock_db.collection('stations').document('LBG').set(lbg)
        self.mock_db.collection('stations').document('SNF').set(snf)
        self.mock_db.collection('destinations').document('LBG').set({
            **lbg,
            'journeys': helpers.make_journey_dict(snf),
            'journey_costs_updated': datetime(2018, 12, 2)
        })

        updaters.update(self.interactor)

        journey = self.mock_db \
            .collection('destinations') \
            .document('LBG') \
            .collection('journeys') \
            .document('SNF') \
            .get().to_dict()

        expected = {
            'min_zone': '1',
            'max_zone': 'SNF',
            'annual_price': 4364
        }
        self.assertEqual(expected, journey['travelcard'])

    def _stub_season_ticket_response(self, price: int):
        stub_response = {'fares': [{
            'ticket': {
                'code': '7DS'
            },
            'adult': {'fare': price * 100}
        }]}

        responses.add(responses.GET, 'http://api.brfares.com/querysimple', json=stub_response)
