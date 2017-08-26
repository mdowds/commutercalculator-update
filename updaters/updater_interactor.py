from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Tuple, Optional

from fnplus import Either, curried

from models import Station
from models.cc_model import CCModel


class UpdaterInteractor:
    __metaclass__ = ABCMeta

    def __init__(self, debug: bool=False) -> None:
        self._debug = debug

    @property
    def debug(self) -> bool:
        return self._debug

    @abstractmethod
    def get_stations_to_update(self) -> Tuple[Station, ...]:
        pass

    @abstractmethod
    def get_all_stations(self) -> Tuple[Station, ...]:
        pass

    @abstractmethod
    def update_dest_record(self, destination: Station, time: datetime) -> Optional[Station]:
        pass

    @abstractmethod
    def get_update(self, destination: Station, origin: Station) -> Either:
        pass

    @abstractmethod
    @curried
    def save_update(self, destination: Station, origin: Station, value) -> CCModel:
        pass