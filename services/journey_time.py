from typing import Union, Tuple

from peewee import fn, SQL
from fn import F
from fnplus import curried, Either, tmap

import interfaces.gmaps as gmaps
from models import JourneyTime
from models import Station
from interfaces.gmaps import JourneyTimeResult


def get_journey_times(destination: Station) -> Tuple[JourneyTimeResult, None]:
    times = JourneyTime\
        .select(JourneyTime.origin, fn.Avg(JourneyTime.time).alias('time'))\
        .join(Station)\
        .where(JourneyTime.destination == destination.sid)\
        .group_by(JourneyTime.origin)\
        .order_by(SQL('time'))

    return tmap(lambda t: JourneyTimeResult(t.origin, t.time), times)


@curried
def update_journey_time(destination: Station, origin: Station) -> Either[JourneyTimeResult]:
    pipe = F() >> gmaps.get_peak_journey_time(destination) >> Either.bind(_save_journey_time(destination))
    return pipe(origin)


@curried
def _save_journey_time(destination: Station, result: JourneyTimeResult) -> JourneyTime:
    return JourneyTime.create(origin=result.origin.sid, destination=destination.sid, time=int(result.time))
