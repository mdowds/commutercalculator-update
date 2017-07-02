from typing import Type, Tuple

from fn import F
from fnplus import tmap, curried

from models import Station, JourneyTime
from interfaces import database as db


@curried
def update_destinations(all_stations: Tuple[Station, ...], destinations: Tuple[Station, ...]) -> Tuple[str, ...]:
    return tmap(lambda s: s.name, destinations)


def update_destination(all_stations: Tuple[Station, ...], destination: Station) -> str:
    return destination.name


def update_journey(destination: Station, origin: Station) -> JourneyTime:
    pass


@curried
def output_message(i):
    return i


pipe = F() >> db.get_stations_to_update() >> update_destinations() >> output_message()
