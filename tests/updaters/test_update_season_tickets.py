from unittest import TestCase

from updaters.season_tickets import *
from tests import helpers


class TestUpdateSeasonTickets(TestCase):

    def setUp(self):
        self._all_stations = helpers.create_station_test_data()

