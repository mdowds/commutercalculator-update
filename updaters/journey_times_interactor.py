from datetime import datetime
from typing import Optional, Iterable

from fn.func import curried
from fn.monad import Either

from interfaces import gmaps
from interfaces.database import Database
from models import Station
from .updater_interactor import UpdaterInteractor


class JourneyTimesInteractor(UpdaterInteractor):

    def __init__(self, db: Database = None, api_key: str = None, debug: bool = False) -> None:
        super().__init__(db, debug)
        self._api_key = api_key

    def get_stations_to_update(self) -> Iterable[Station]:
        return self.db.get_stations_for_journey_time_update()

    def get_all_stations(self) -> Iterable[Station]:
        return self.db.get_all_stations()

    def update_dest_record(self, destination: Station, time: datetime) -> Optional[Station]:
        return self.db.update_journey_times_updated(destination, time)

    def get_update(self, destination: Station, origin: Station) -> Either[int]:
        return gmaps.get_peak_journey_time(self._api_key, destination, origin)

    @curried
    def save_update(self, destination: Station, origin: Station, value: int):
        return self.db.save_journey_time(destination, origin, value)
