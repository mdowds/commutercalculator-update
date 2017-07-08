from typing import Tuple

from models import Station, JourneyTime


def get_stations_to_update() -> Tuple[Station, ...]:
    return Station.select() \
        .where((Station.min_zone == 1) | (Station.max_zone == 1)) \
        .order_by(Station.journey_times_updated)\
        .limit(3)


def get_all_stations() -> Tuple[Station, ...]:
    return Station.select().order_by(Station.name)


def save_journey_time(destination: Station, origin: Station, time: int) -> JourneyTime:
    return JourneyTime.create(origin=origin.sid, destination=destination.sid, time=int(time))
