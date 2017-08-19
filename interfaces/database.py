from typing import Tuple
from datetime import datetime

from fnplus import curried
from peewee import fn

from models import Station, JourneyTime, SeasonTicket


def get_stations_for_journey_time_update() -> Tuple[Station, ...]:
    return Station.select() \
        .where((Station.min_zone == 1) | (Station.max_zone == 1)) \
        .order_by(Station.journey_times_updated)\
        .limit(3)


def get_station_for_season_ticket_update() -> Station:
    res = Station.select()\
        .join(SeasonTicket)\
        .where(
            (Station.min_zone == 1) | (Station.max_zone == 1),
            Station.modes == 'NR'
        )\
        .group_by(Station)\
        .having(fn.Count(SeasonTicket.destination) > 0)\
        .limit(1)

    return res[0]


def get_all_stations() -> Tuple[Station, ...]:
    return Station.select().order_by(Station.name)


@curried
def save_journey_time(destination: Station, origin: Station, time: int) -> JourneyTime:
    return JourneyTime.create(origin=origin.sid, destination=destination.sid, time=int(time))


def update_journey_times_updated(station: Station, timestamp: datetime) -> Station:
    station.journey_times_updated = timestamp
    station.save()
    return station
