import os
import json

from unittest import TestCase
from unittest.mock import patch

from tests import helpers
from interfaces.brfares import *


class TestBrFares(TestCase):

    @patch('interfaces.brfares.requests')
    def test_get_season_ticket_annual_price(self, mock_requests):
        mock_requests.get.return_value = MockRequest()
        stations = helpers.create_station_test_data()

        self.assertEqual(728, get_season_ticket_annual_price(stations[0], stations[1]).value())


class MockRequest:
    def json(self):
        data_file = os.path.join(os.getcwd(), 'tests', 'interfaces', 'data', 'brfares_response.json')
        with open(data_file, 'r') as file:
            return json.load(file)
