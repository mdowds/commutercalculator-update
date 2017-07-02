from typing import Type, Tuple

from fnplus import curried

from models import Station, JourneyTime


@curried
def get_stations_to_update(station_model: Type[Station]) -> Tuple[Station, ...]:
    return station_model.select() \
        .where((Station.min_zone == 1) | (Station.max_zone == 1)) \
        .order_by(Station.journey_times_updated)\
        .limit(3)


def get_all_stations(station_model: Type[Station]) -> Tuple[Station, ...]:
    return station_model.select().order_by(Station.name)


def save_journey_time(destination: Station, origin: Station, time: int) -> JourneyTime:
    return JourneyTime.create(origin=origin.sid, destination=destination.sid, time=int(time))
