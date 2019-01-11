from datetime import datetime
from functools import reduce
from typing import Tuple, NamedTuple, TypeVar, Callable, Iterable

from fn.func import curried
from fn.iters import filter_tuple, map_tuple
from fn.monad import Either

from models import Station
from .updater_interactor import UpdaterInteractor

UpdateResponse = NamedTuple('UpdateResponse', (('updates', int), ('errors', int)))
UpdateOutput = NamedTuple('UpdateOutput', (('message', str), ('has_errors', bool)))


def update(interactor: UpdaterInteractor) -> UpdateOutput:
    update_results = _update_destinations(interactor)
    has_errors = update_results[2] > 0
    return UpdateOutput(_output_message(update_results), has_errors)


def _update_destinations(interactor: UpdaterInteractor) -> Tuple[int, int, int]:
    destinations = interactor.get_stations_to_update()
    all_update_responses = map_tuple(_update_destination(interactor), destinations)

    updates = sum((response.updates for response in all_update_responses))
    errors = sum((response.errors for response in all_update_responses))

    return len(all_update_responses), updates, errors


@curried
def _update_destination(interactor: UpdaterInteractor, destination: Station) -> UpdateResponse:
    all_stations = interactor.get_all_stations()
    origins = filter_tuple(lambda s: s.sid != destination.sid, all_stations)

    journeys = map_tuple(_update_journey(interactor, destination), origins)

    for journey in journeys:
        if journey.error is not None:
            print(journey.error_type)
            print(journey.error)

    updates = _conditional_len(lambda j: j.error is None, journeys)
    errors = len(journeys) - updates

    if updates / len(journeys) > 0.9 and interactor.update_dest_record:
        interactor.update_dest_record(destination, datetime.now())

    return UpdateResponse(updates, errors)


@curried
def _update_journey(interactor: UpdaterInteractor, destination: Station, origin: Station) -> Either:
    print("Updating from " + origin.name + " to " + destination.name)

    journey = interactor.get_update(destination, origin)

    return journey >> interactor.save_update(destination, origin)


def _output_message(results: Tuple[int, int, int]) -> str:
    stations = str(results[0])
    journeys = str(results[1])
    errors = str(results[2])

    return stations + " stations updated with " + journeys + " records created and " + errors + " errors"


T = TypeVar('T')
def _conditional_len(cond: Callable[[T], bool], seq: Iterable[T]) -> int:
    return reduce(lambda length, x: length + 1 if cond(x) else length, seq, 0)
