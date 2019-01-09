from datetime import datetime
from typing import Tuple, Any, Dict, List

from models import Station
from tests.mockfirestore import GeoPoint


def make_datetime(day):
    return datetime.strptime(day + ' 06 2016', '%d %m %Y')


def create_station_test_data() -> Tuple[Station, ...]:
    def _station(sid, name):
        return Station(
            sid=sid,
            name=name,
            lat=1.0, long=1.0
        )

    return (
        _station('FOO', 'Foo'),
        _station('BAR', 'Bar'),
        _station('BAZ', 'Baz'),
        _station('FOZ', 'Foz')
    )


def make_station_dict(sid: str, name: str, location: GeoPoint = GeoPoint(0.0, 0.0), zones: List[int] = []) -> Dict[
    str, Any]:
    return {
        'sid': sid,
        'name': name,
        'location': location,
        'zones': zones
    }


def make_journey_dict(origin: Dict[str, Any]) -> Dict[str, Any]:
    return {
        origin['sid']: {
            'origin': origin
        }
    }

# def create_season_ticket_test_data() -> Tuple[SeasonTicket, ...]:
#     return (
#         SeasonTicket(destination='FOO', origin='FOZ', annual_price=1000),
#         SeasonTicket(destination='FOO', origin='BAZ', annual_price=1500)
#     )
