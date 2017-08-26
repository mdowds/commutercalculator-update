from datetime import datetime
from typing import Tuple, Optional

from fnplus import Either, curried

from models import Station, SeasonTicket
from .updater_interactor import UpdaterInteractor
from interfaces import database as db, brfares


class SeasonTicketsInteractor(UpdaterInteractor):

    def get_stations_to_update(self) -> Tuple[Station, ...]:
        return tuple([db.get_station_for_season_ticket_update()])

    def get_all_stations(self) -> Tuple[Station, ...]:
        return db.get_all_nr_stations()

    def get_update(self, destination: Station, origin: Station) -> Either[int]:
        if self.debug: return Either(10)
        return brfares.get_season_ticket_annual_price(destination, origin)

    def update_dest_record(self, destination: Station, time: datetime) -> Optional[Station]:
        pass

    @curried
    def save_update(self, destination: Station, origin: Station, value: int) -> SeasonTicket:
        return db.save_season_ticket(destination, origin, value)
