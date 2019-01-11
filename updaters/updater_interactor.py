from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Optional, Iterable

from fn.func import curried
from fn.monad import Either

from interfaces.database import Database
from models import Station


class UpdaterInteractor:
    __metaclass__ = ABCMeta

    def __init__(self, db: Database, debug: bool = False) -> None:
        self.db = db
        self._debug = debug

    @property
    def debug(self) -> bool:
        return self._debug

    @abstractmethod
    def get_stations_to_update(self) -> Iterable[Station]:
        pass

    @abstractmethod
    def get_all_stations(self) -> Iterable[Station]:
        pass

    @abstractmethod
    def update_dest_record(self, destination: Station, time: datetime) -> Optional[Station]:
        pass

    @abstractmethod
    def get_update(self, destination: Station, origin: Station) -> Either:
        pass

    @abstractmethod
    @curried
    def save_update(self, destination: Station, origin: Station, value):
        pass
