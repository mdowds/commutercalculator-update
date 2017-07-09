from typing import Tuple, Callable, NamedTuple, Iterable, TypeVar
from functools import reduce
from datetime import datetime

from fn import F
from fnplus import tmap, curried, Either, tfilter

from models import Station, JourneyTime
from interfaces import database as db, gmaps


GetTimeFunc = Callable[[Station, Station], Either[int]]
SaveJourneyFunc = Callable[[Station, Station, int], JourneyTime]
UpdateDestRecordFunc = Callable[[Station, datetime], Station]
UpdateResponse = NamedTuple('UpdateResponse', (('updates', int), ('errors', int)))


@curried
def update_destinations(get_time: GetTimeFunc,
                        save_journey: SaveJourneyFunc,
                        update_dest_record: UpdateDestRecordFunc,
                        all_stations: Tuple[Station, ...],
                        destinations: Tuple[Station, ...]
                        ) -> Tuple[int, int, int]:
    all_update_responses = tmap(update_destination(get_time, save_journey, update_dest_record, all_stations), destinations)

    updates = reduce(
        lambda updates, updates_for_dest: updates + updates_for_dest.updates,
        all_update_responses, 0)

    errors = reduce(
        lambda errors, updates_for_dest: errors + updates_for_dest.errors,
        all_update_responses, 0)

    return (len(all_update_responses), updates, errors)


@curried
def update_destination(get_time: GetTimeFunc,
                        save_journey: SaveJourneyFunc,
                        update_dest_record: UpdateDestRecordFunc,
                        all_stations: Tuple[Station, ...],
                        destination: Station
                    ) -> UpdateResponse:
    update = _update_journey(get_time, save_journey, destination)
    origins = tfilter(lambda s: s.sid != destination.sid, all_stations)

    journeys = tmap(update, origins)

    updates = conditional_len(lambda j: j.get_error() is None, journeys)
    errors = len(journeys) - updates

    if updates / len(journeys) > 0.9:
        update_dest_record(destination, datetime.now())

    return UpdateResponse(updates, errors)


@curried
def _update_journey(get_time: GetTimeFunc,
                       save_journey: SaveJourneyFunc,
                       destination: Station,
                       origin: Station
                   ) -> Either[JourneyTime]:
    journey_time = get_time(destination, origin)
    return Either.try_bind(save_journey(destination, origin))(journey_time)


@curried
def output_message(i):
    return i


T = TypeVar('T')
def conditional_len(cond: Callable[[T], bool], seq: Iterable[T]) -> int:
    return reduce(lambda len, x: len+1 if cond(x) else len, seq, 0)


def conditional_sum(cond: Callable[[int], bool], seq: Iterable[T]) -> int:
    return reduce(lambda len, x: len+1 if cond(x) else len, seq, 0)


pipe = F() >> db.get_stations_to_update() >> update_destinations(gmaps.get_peak_journey_time, db.get_all_stations()) >> output_message()
