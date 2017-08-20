from datetime import datetime
from typing import Tuple

from models import Station, SeasonTicket


def make_datetime(day):
    return datetime.strptime(day + ' 06 2016', '%d %m %Y')


def create_station_test_data() -> Tuple[Station, ...]:
    def _station(sid, name, min_zone=1, max_zone=1, day_updated='01', modes=''):
        return Station(
            sid=sid,
            name=name,
            min_zone=min_zone,
            max_zone=max_zone,
            journey_times_updated=make_datetime(day_updated),
            lat=1.0, long=1.0,
            postcode="N1",
            major_station=True,
            modes=modes
        )

    return (
        _station('FOO', 'Foo', 1, 1, '10', 'NR'),
        _station('BAR', 'Bar', 1, 1, '05'),
        _station('BAZ', 'Baz', 1, 2, '12', 'NR'),
        _station('FOZ', 'Foz', 2, 2, '09', 'NR')
    )

def create_season_ticket_test_data() -> Tuple[SeasonTicket, ...]:
    return (
        SeasonTicket(destination='FOO', origin='FOZ', annual_price=1000),
        SeasonTicket(destination='FOO', origin='BAZ', annual_price=1500)
    )
