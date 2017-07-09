from datetime import datetime

from models import Station


def make_datetime(day):
    return datetime.strptime(day + ' 06 2016', '%d %m %Y')

def create_test_data():
    def _station(sid, name, min_zone=1, max_zone=1, day_updated='01'):
        return Station(
            sid=sid,
            name=name,
            min_zone=min_zone,
            max_zone=max_zone,
            journey_times_updated=make_datetime(day_updated),
            lat=1.0, long=1.0, postcode="N1", major_station=True)

    return (
        _station('FOO', 'Foo', 1, 1, '10'),
        _station('BAR', 'Bar', 1, 1, '05'),
        _station('BAZ', 'Baz', 1, 2, '12'),
        _station('FOZ', 'Foz', 2, 2, '09')
    )
