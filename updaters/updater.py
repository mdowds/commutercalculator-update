from functools import reduce
from typing import Tuple, NamedTuple, TypeVar, Callable, Iterable
from datetime import datetime

from fnplus import Either, tmap, tfilter, curried

from models import Station
from .updater_interactor import UpdaterInteractor

UpdateResponse = NamedTuple('UpdateResponse', (('updates', int), ('errors', int)))


def update(interactor: UpdaterInteractor) -> str:
    update_results = _update_destinations(interactor)
    return _output_message(update_results)


def _update_destinations(interactor: UpdaterInteractor) -> Tuple[int, int, int]:
    destinations = interactor.get_stations_to_update()
    all_update_responses = tmap(_update_destination(interactor), destinations)

    updates = sum((response.updates for response in all_update_responses))
    errors = sum((response.errors for response in all_update_responses))

    return (len(all_update_responses), updates, errors)


@curried
def _update_destination(interactor: UpdaterInteractor, destination: Station) -> UpdateResponse:
    all_stations = interactor.get_all_stations()
    origins = tfilter(lambda s: s.sid != destination.sid, all_stations)

    journeys = tmap(_update_journey(interactor, destination), origins)

    updates = _conditional_len(lambda j: j.error is None, journeys)
    errors = len(journeys) - updates

    if updates / len(journeys) > 0.9 and interactor.update_dest_record:
        interactor.update_dest_record(destination, datetime.now())

    return UpdateResponse(updates, errors)


@curried
def _update_journey(interactor: UpdaterInteractor, destination: Station, origin: Station) -> Either:
    if interactor.debug: print("Updating from " + origin.name + " to " + destination.name)

    journey = interactor.get_update(destination, origin)
    return journey.try_call(interactor.save_update(destination, origin))


def _output_message(results: Tuple[int, int, int]) -> str:
    stations = str(results[0])
    journeys = str(results[1])
    errors = str(results[2])

    return stations + " stations updated with " + journeys + " records created and " + errors + " errors"


T = TypeVar('T')
def _conditional_len(cond: Callable[[T], bool], seq: Iterable[T]) -> int:
    return reduce(lambda len, x: len+1 if cond(x) else len, seq, 0)
