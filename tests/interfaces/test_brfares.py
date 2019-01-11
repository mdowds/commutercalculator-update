from unittest import TestCase

from interfaces.brfares import _extract_weekly_fare, _calculate_annual_fare


class TestBrFares(TestCase):

    def test_extract_weekly_fare(self):
        response = {'fares': [{
            'ticket': {
                'code': '7DS'
            },
            'adult': {'fare': 7200}
        }]}

        self.assertEqual(7200, _extract_weekly_fare(response))
        
    def test_extract_weekly_fare_noWeeklyFareAvailable(self):
        response = {'fares': [{
            'ticket': {
                'code': '1DS'
            },
            'adult': {'fare': 1000}
        }]}

        self.assertIsNone(_extract_weekly_fare(response))
        
    def test_calculate_annual_fare(self):
        self.assertEqual(1200, _calculate_annual_fare(3000))

