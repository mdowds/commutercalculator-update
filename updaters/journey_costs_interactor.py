from datetime import datetime
from typing import Optional, TypeVar, Iterable

from fn.func import curried
from fn.iters import filter, first, sort
from fn.monad import Either, Pipe

from exceptions import JourneyCostError
from models import Station, Travelcard
from .updater_interactor import UpdaterInteractor


class JourneyCostsInteractor(UpdaterInteractor):

    def get_stations_to_update(self) -> Iterable[Station]:
        return self.db.get_stations_for_journey_costs_update()

    def get_all_stations(self) -> Iterable[Station]:
        return self.db.get_all_stations()

    def get_update(self, destination: Station, origin: Station) -> Either[Travelcard]:
        return Either.fromfunction(self._get_cheapest_travelcard, destination, origin)

    def update_dest_record(self, destination: Station, time: datetime) -> Optional[Station]:
        return self.db.update_journey_costs_updated(destination, time)

    @curried
    def save_update(self, destination: Station, origin: Station, value: Travelcard):
        return self.db.save_travelcard_price(destination, origin, value)

    def _get_cheapest_travelcard(self, destination: Station, origin: Station) -> Travelcard:
        possible_travelcards = (
            Travelcard.for_zones(min_zone=max(destination.zones), max_zone=min(origin.zones)),
            Travelcard.for_zones(min_zone=min(destination.zones), max_zone=min(origin.zones))
        )

        filter_null_results = filter(lambda tc: tc is not None)

        cheapest: Pipe[Travelcard] = Pipe(possible_travelcards) >> \
            filter_null_results >> \
            sort(lambda tc: tc.annual_price) >> \
            first

        if cheapest.value is None:
            raise JourneyCostError("No travelcard found for {} to {}".format(origin.name, destination.name))

        return cheapest.value


T = TypeVar('T')
