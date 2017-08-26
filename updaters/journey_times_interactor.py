from datetime import datetime
from typing import Tuple

from fnplus import Either, curried

from models import Station, JourneyTime
from .updater_interactor import UpdaterInteractor
from interfaces import database as db, gmaps


class JourneyTimesInteractor(UpdaterInteractor):

    def __init__(self, api_key: str = None, debug: bool = False):
        super().__init__(debug)
        self._api_key = api_key

    def get_stations_to_update(self) -> Tuple[Station, ...]:
        return db.get_stations_for_journey_time_update()

    def get_all_stations(self) -> Tuple[Station, ...]:
        return db.get_all_stations()

    def update_dest_record(self, destination: Station, time: datetime) -> Station:
        return db.update_journey_times_updated(destination, time)

    def get_update(self, destination: Station, origin: Station) -> Either[int]:
        if self.debug: return Either(10)
        return gmaps.get_peak_journey_time(self._api_key, destination, origin)

    @curried
    def save_update(self, destination: Station, origin: Station, value: int) -> JourneyTime:
        return db.save_journey_time(destination, origin, value)
