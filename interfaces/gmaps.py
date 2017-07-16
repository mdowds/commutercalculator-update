from datetime import date, time, datetime, timedelta
from typing import Any, Dict, Iterable
from functools import reduce

from pytz import timezone
import googlemaps
from fnplus import curried, Either
from fn import F

from models import Station


@curried
def get_peak_journey_time(api_key: str, destination: Station, origin: Station) -> Either[int]:
    pipe = F() >> _get_peak_time >> _directions_request(api_key, origin, destination) >> _extract_journey_time
    return pipe(date.today())

# Helpers

@curried
def _directions_request(api_key: str, origin: Station, destination: Station, arrival_time: int=None) -> Either[Dict]:
    @curried
    def _request(origin, destination, arrival_time, g) -> Either[Dict]:
        return g.directions(
            "%s,%s" % (origin.lat, origin.long),
            "%s,%s" % (destination.lat, destination.long),
            mode="transit",
            arrival_time=arrival_time
        )

    directions = F() >> Either.try_(googlemaps.Client) >> Either.try_bind(_request(origin, destination, arrival_time))

    return directions(api_key)


@curried
def _extract_journey_time(response: Either[Dict]) -> Either[int]:
    pipe = F() >> Either.bind(_dict_path((0, "legs", 0, "duration", "value"))) >> Either.bind(lambda t: int(t/60))
    return pipe(response)


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
        try: return dictionary[key]
        except (KeyError, TypeError, IndexError): return None

    return reduce(select, keys, input_dict)
