from datetime import datetime
from typing import Tuple

from models import Station


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

# def create_season_ticket_test_data() -> Tuple[SeasonTicket, ...]:
#     return (
#         SeasonTicket(destination='FOO', origin='FOZ', annual_price=1000),
#         SeasonTicket(destination='FOO', origin='BAZ', annual_price=1500)
#     )
