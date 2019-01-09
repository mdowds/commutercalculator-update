import unittest
from interfaces.gmaps import *
from interfaces.gmaps import _extract_journey_time, _get_peak_time, _next_weekday, _dict_path
import datetime


class TestGmapsInterface(unittest.TestCase):
    origin = Station(sid="FOO", lat=1.5, long=-0.2, name="Foo", zones=[])
    dest = Station(sid="BAR", lat=1.6, long=-0.3, name="Bar", zones=[])

    def test_extract_journey_time(self):
        response = {"routes": [{"legs": [{"duration": {"value": 600}}]}]}
        self.assertEqual(10, _extract_journey_time(response))

    def test_get_peak_time(self):
        self.assertEqual(1495526400, _get_peak_time(datetime.date(2017, 5, 22)))
        self.assertEqual(1495440000, _get_peak_time(datetime.date(2017, 5, 19)))

    def test_next_weekday(self):
        self.assertEqual("Tue", _next_weekday(datetime.date(2017, 5, 22)).strftime("%a"))
        self.assertEqual("Mon", _next_weekday(datetime.date(2017, 5, 26)).strftime("%a"))
        self.assertEqual("Mon", _next_weekday(datetime.date(2017, 5, 27)).strftime("%a"))

    def test_dict_path(self):
        dict1 = {"foo": "bar"}
        dict2 = {2: 4}

        self.assertEqual("bar", _dict_path(["foo"], dict1))
        self.assertEqual(4, _dict_path([2], dict2))

    def test_dict_path_withNestedDict(self):
        dict1 = {"foo": {"bar": "baz"}}
        dict2 = {"foo": {"bar": {"baz": "foz"}}}
        dict3 = {1: {2: 3}}

        self.assertEqual("baz", _dict_path(("foo", "bar"), dict1))
        self.assertEqual("foz", _dict_path(("foo", "bar", "baz"), dict2))
        self.assertEqual(3, _dict_path((1, 2), dict3))

    def test_dict_path_withArrayInDict(self):
        dict1 = {"foo": [{"bar": "baz"}]}
        self.assertEqual("baz", _dict_path(("foo", 0, "bar"), dict1))

    def test_dict_path_withMissingKey(self):
        self.assertEqual(None, _dict_path("foo", {}))
