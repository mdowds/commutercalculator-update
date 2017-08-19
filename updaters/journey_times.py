from typing import Tuple, Callable, NamedTuple, Iterable, TypeVar
from functools import reduce
from datetime import datetime

from fnplus import tmap, curried, Either, tfilter

from models import Station, JourneyTime
from interfaces import database as db, gmaps

GetTimeFunc = Callable[[Station, Station], Either[int]]
SaveJourneyFunc = Callable[[Station, Station, int], JourneyTime]
UpdateDestRecordFunc = Callable[[Station, datetime], Station]

UpdateResponse = NamedTuple('UpdateResponse', (('updates', int), ('errors', int)))


def journey_times(api_key: str=None, debug: bool=False) -> str:
    stations_to_update = db.get_stations_for_journey_time_update()
    all_stations = db.get_all_stations()

    get_time = (lambda d, o: Either(10)) if debug else gmaps.get_peak_journey_time(api_key)

    update_results = _update_destinations(
        get_time,
        db.save_journey_time,
        db.update_journey_times_updated,
        all_stations,
        stations_to_update
    )

    return _output_message(update_results)


def _update_destinations(get_time: GetTimeFunc,
                         save_journey: SaveJourneyFunc,
                         update_dest_record: UpdateDestRecordFunc,
                         all_stations: Tuple[Station, ...],
                         destinations: Tuple[Station, ...]
                         ) -> Tuple[int, int, int]:
    all_update_responses = tmap(_update_destination(get_time, save_journey, update_dest_record, all_stations), destinations)

    updates = reduce(
        lambda updates, updates_for_dest: updates + updates_for_dest.updates,
        all_update_responses, 0)

    errors = reduce(
        lambda errors, updates_for_dest: errors + updates_for_dest.errors,
        all_update_responses, 0)

    return (len(all_update_responses), updates, errors)


@curried
def _update_destination(get_time: GetTimeFunc,
                        save_journey: SaveJourneyFunc,
                        update_dest_record: UpdateDestRecordFunc,
                        all_stations: Tuple[Station, ...],
                        destination: Station
                        ) -> UpdateResponse:
    origins = tfilter(lambda s: s.sid != destination.sid, all_stations)

    journeys = tmap(_update_journey(get_time, save_journey, destination), origins)

    updates = _conditional_len(lambda j: j.get_error() is None, journeys)
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
    # print("Updating from " + origin.name + " to " + destination.name)
    journey_time = get_time(destination, origin)
    return Either.try_bind(save_journey(destination, origin))(journey_time)


def _output_message(results: Tuple[int,int,int]) -> str:
    stations = str(results[0])
    journeys = str(results[1])
    errors = str(results[2])

    return stations + " stations updated with " + journeys + " journey records created and " + errors + " errors"


T = TypeVar('T')
def _conditional_len(cond: Callable[[T], bool], seq: Iterable[T]) -> int:
    return reduce(lambda len, x: len+1 if cond(x) else len, seq, 0)
