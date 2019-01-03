from datetime import datetime
from typing import Tuple, Optional

from fnplus import Either, curried

from interfaces.database import Database
from models import Station
from .updater_interactor import UpdaterInteractor
from interfaces import gmaps


class JourneyTimesInteractor(UpdaterInteractor):

    def __init__(self, db: Database = None, api_key: str = None, debug: bool = False) -> None:
        super().__init__(debug)
        self._api_key = api_key
        self._db = db

    def get_stations_to_update(self) -> Tuple[Station, ...]:
        return self._db.get_stations_for_journey_time_update()

    def get_all_stations(self) -> Tuple[Station, ...]:
        return self._db.get_all_stations()

    def update_dest_record(self, destination: Station, time: datetime) -> Optional[Station]:
        return self._db.update_journey_times_updated(destination, time)

    def get_update(self, destination: Station, origin: Station) -> Either[int]:
        if self.debug: return Either(10)
        return gmaps.get_peak_journey_time(self._api_key, destination, origin)

    @curried
    def save_update(self, destination: Station, origin: Station, value: int):
        return self._db.save_journey_time(destination, origin, value)
