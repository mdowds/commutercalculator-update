from datetime import date, time, datetime, timedelta
from typing import Any, Dict, Iterable
from functools import reduce

import requests
from pytz import timezone
from fn.monad import Either, Pipe
from fn.func import curried

from models import Station


@curried
def get_peak_journey_time(api_key: str, destination: Station, origin: Station) -> Either[int]:
    return Either(date.today()) >> \
           _get_peak_time >> \
           _directions_request(api_key, origin, destination) >> \
           _extract_journey_time


# Helpers

@curried
def _directions_request(api_key: str, origin: Station, destination: Station, arrival_time: int = None) -> Dict[str, Any]:
    r = requests.get('https://maps.googleapis.com/maps/api/directions/json', params={
        'origin': '%s,%s' % (origin.lat, origin.long),
        'destination': '%s,%s' % (destination.lat, destination.long),
        'mode': 'transit',
        'arrival_time': arrival_time,
        'key': api_key
    })
    return r.json()


@curried
def _extract_journey_time(response: Dict[str, Any]) -> int:
    pipe = Pipe(response) >> _dict_path(("routes", 0, "legs", 0, "duration", "value")) >> (lambda t: int(t / 60))
    return pipe.value


def _get_peak_time(base_date: date) -> int:
    day = _next_weekday(base_date)
    dt = datetime.combine(day, time(9))
    localised = timezone('Europe/London').localize(dt)
    return int(localised.timestamp())


def _next_weekday(base_date: date) -> date:
    def is_weekday(date_to_check: date) -> bool:
        return date_to_check.weekday() in range(0, 5)

    next_date = base_date + timedelta(1)
    return next_date if is_weekday(next_date) else _next_weekday(next_date)


@curried
def _dict_path(keys: Iterable[Any], input_dict: Dict[Any, Any]) -> Any:
    def select(dictionary, key):
        try:
            return dictionary[key]
        except (KeyError, TypeError, IndexError):
            return None

    return reduce(select, keys, input_dict)
