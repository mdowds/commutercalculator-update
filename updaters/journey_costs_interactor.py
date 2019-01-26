from datetime import datetime
from typing import Optional, TypeVar, Iterable, Tuple

from fn.func import curried
from fn.iters import filter, first, sort
from fn.monad import Either, Pipe

from exceptions import JourneyCostError
from interfaces.brfares import get_season_ticket
from models import Station, Travelcard, SeasonTicket, JourneyCosts
from .updater_interactor import UpdaterInteractor


class JourneyCostsInteractor(UpdaterInteractor):

    def get_stations_to_update(self) -> Iterable[Station]:
        return self.db.get_stations_for_journey_costs_update()

    def get_all_stations(self) -> Iterable[Station]:
        return self.db.get_all_stations()

    def get_update(self, destination: Station, origin: Station) -> Either[JourneyCosts]:
        season_ticket = self._get_season_ticket(destination, origin)
        return Either.fromfunction(self._add_cheapest_travelcard, destination, origin, season_ticket)

    @curried
    def save_update(self, destination: Station, origin: Station, value: JourneyCosts):
        return self.db.save_journey_costs(destination, origin, value)

    def update_dest_record(self, destination: Station, time: datetime) -> Optional[Station]:
        return self.db.update_journey_costs_updated(destination, time)

    def _get_season_ticket(self, origin: Station, destination: Station) -> Optional[SeasonTicket]:
        if 'NR' not in origin.modes or 'NR' not in destination.modes:
            return None

        season_ticket = get_season_ticket(destination, origin)

        if season_ticket.is_error:
            print("Error fetching season ticket for {} to {}:".format(origin.name, destination.name))
            print(season_ticket.error)

        return season_ticket.value

    @curried
    def _add_cheapest_travelcard(self, destination: Station, origin: Station, season_ticket: Optional[SeasonTicket]) -> JourneyCosts:

        possible_travelcards = self._get_possible_travelcards(destination, origin)

        filter_null_results = filter(lambda tc: tc is not None)

        cheapest: Pipe[Travelcard] = Pipe(possible_travelcards) >> \
            filter_null_results >> \
            sort(lambda tc: tc.annual_price) >> \
            first

        if cheapest.value is None:
            raise JourneyCostError("No travelcard found for {} to {}".format(origin.name, destination.name))

        return JourneyCosts(season_ticket, cheapest.value)

    def _get_possible_travelcards(self, destination, origin) -> Tuple[Travelcard, ...]:

        dest_max_zone = str(max(destination.zones))

        if len(origin.zones) == 0:
            return Travelcard.for_zones(min_zone=dest_max_zone, max_zone=origin.sid),

        origin_min_zone = str(min(origin.zones))
        origin_max_zone = str(max(origin.zones))
        dest_min_zone = str(min(destination.zones))

        return (
            Travelcard.for_zones(min_zone=dest_max_zone, max_zone=origin_min_zone),
            Travelcard.for_zones(min_zone=dest_max_zone, max_zone=origin_max_zone),
            Travelcard.for_zones(min_zone=dest_min_zone, max_zone=origin_min_zone)
        )

