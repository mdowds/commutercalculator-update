from typing import Tuple, Callable, NamedTuple, Iterable, TypeVar
from functools import reduce

from fnplus import tmap, curried, Either, tfilter

from models import Station, SeasonTicket
from interfaces import database as db, brfares

GetPriceFunc = Callable[[Station, Station], Either[int]]
SaveSeasonTicketFunc = Callable[[Station, Station, int], SeasonTicket]

UpdateResponse = NamedTuple('UpdateResponse', (('updates', int), ('errors', int)))


def season_tickets(debug: bool=False) -> str:
    station_to_update = db.get_station_for_season_ticket_update()
    all_stations = db.get_all_nr_stations()
    get_price = (lambda d, o: Either(10)) if debug else brfares.get_season_ticket_annual_price

    update_results = _update_destination(
        get_price,
        db.save_season_ticket,
        all_stations,
        station_to_update
    )

    results = (update_results.updates + update_results.errors, update_results.updates, update_results.errors)

    return _output_message(results)


@curried
def _update_destination(get_price: GetPriceFunc,
                        save_season_ticket: SaveSeasonTicketFunc,
                        all_stations: Tuple[Station, ...],
                        destination: Station
                        ) -> UpdateResponse:
    origins = tfilter(lambda s: s.sid != destination.sid, all_stations)

    season_ticket_prices = tmap(_update_season_ticket(get_price, save_season_ticket, destination), origins)

    updates = _conditional_len(lambda j: j.error() is None, season_ticket_prices)
    errors = len(season_ticket_prices) - updates

    return UpdateResponse(updates, errors)


@curried
def _update_season_ticket(get_price: GetPriceFunc,
                          save_season_ticket: SaveSeasonTicketFunc,
                          destination: Station,
                          origin: Station
                          ) -> Either[SeasonTicket]:
    print("Updating from " + origin.name + " to " + destination.name)
    journey_time = get_price(destination, origin)
    return journey_time.try_call(save_season_ticket(destination, origin))


def _output_message(results: Tuple[int,int,int]) -> str:
    stations = str(results[0])
    prices = str(results[1])
    errors = str(results[2])

    return stations + " station updated with " + prices + " season ticket records created and " + errors + " errors"


T = TypeVar('T')
def _conditional_len(cond: Callable[[T], bool], seq: Iterable[T]) -> int:
    return reduce(lambda len, x: len+1 if cond(x) else len, seq, 0)
