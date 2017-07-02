from typing import Type, Tuple

from fn import F
from fnplus import tmap, curried

from models import Station


@curried
def get_stations(station_model: Type[Station]) -> Tuple[Station]:
    return station_model.select() \
        .where((Station.min_zone == 1) | (Station.max_zone == 1)) \
        .order_by(Station.journey_times_updated)\
        .limit(3)


@curried
def update_stations(i):
    return i


@curried
def output_message(i):
    return i


pipe = F() >> get_stations() >> update_stations() >> output_message()
