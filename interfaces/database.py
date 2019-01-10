from typing import Tuple, Iterable
from datetime import datetime, date

from fn.func import curried
from fn.iters import map
from google.cloud.firestore_v1beta1 import DocumentSnapshot, DocumentReference, CollectionReference
from google.cloud import firestore

from models import Station, Travelcard


class Database:
    def __init__(self, firestore: firestore.Client):
        self._firestore = firestore

    @property
    def _destinations(self) -> CollectionReference:
        return self._firestore.collection('destinations')

    @property
    def _stations(self) -> CollectionReference:
        return self._firestore.collection('stations')

    def get_stations_for_journey_time_update(self) -> Tuple[Station, ...]:
        docs: Iterable[DocumentSnapshot] = self._destinations\
            .order_by('journey_times_updated')\
            .limit(1)\
            .get()

        return map(lambda doc: Station.from_dict(doc.to_dict()), docs)

    def get_stations_for_journey_costs_update(self) -> Tuple[Station, ...]:
        this_year = date.today().year
        docs: Iterable[DocumentSnapshot] = self._destinations\
            .where('journey_costs_updated', '<', datetime(this_year, 1, 1))\
            .order_by('journey_costs_updated')\
            .limit(1).get()

        return map(lambda doc: Station.from_dict(doc.to_dict()), docs)

    def get_all_stations(self) -> Tuple[Station]:
        docs: Iterable[DocumentSnapshot] = self._stations.get()
        return map(lambda doc: Station.from_dict(doc.to_dict()), docs)

    @curried
    def save_journey_time(self, destination: Station, origin: Station, time: int):
        destination_ref: DocumentReference = self._firestore.collection('destinations').document(destination.sid)
        journey_ref: DocumentReference = destination_ref.collection('journeys').document(origin.sid)

        if journey_ref.get().exists:
            return journey_ref.update({'time': time})
        else:
            return journey_ref.set({
                'origin': self._stations.document(origin.sid).get().to_dict(),
                'time': time
            })

    def save_travelcard_price(self, destination: Station, origin: Station, travelcard: Travelcard):
        destination_ref: DocumentReference = self._firestore.collection('destinations').document(destination.sid)
        journey_ref: DocumentReference = destination_ref.collection('journeys').document(origin.sid)

        if journey_ref.get().exists:
            return journey_ref.update({'travelcard': travelcard.to_dict()})
        else:
            return journey_ref.set({
                'origin': self._stations.document(origin.sid).get().to_dict(),
                'travelcard': travelcard.to_dict()
            })

    def update_journey_times_updated(self, destination: Station, timestamp: datetime):
        self._destinations.document(destination.sid).update({
            'journey_times_updated': timestamp
        })

    def update_journey_costs_updated(self, destination: Station, timestamp: datetime):
        self._destinations.document(destination.sid).update({
            'journey_costs_updated': timestamp
        })

# def get_station_for_season_ticket_update() -> Station:
#     res = Station.select(Station)\
#         .join(SeasonTicket, JOIN.LEFT_OUTER)\
#         .where(
#             (Station.min_zone == 1) | (Station.max_zone == 1),
#             Station.modes == 'NR'
#         )\
#         .group_by(Station)\
#         .having(fn.Count(SeasonTicket.destination) == 0)\
#         .limit(1)
#
#     return res[0]
#
# def get_all_nr_stations() -> Tuple[Station, ...]:
#     return Station.select().where(Station.modes == 'NR')
#
#
# @curried
# def save_season_ticket(destination: Station, origin: Station, annual_price: int) -> SeasonTicket:
#     return SeasonTicket.create(origin=origin.sid, destination=destination.sid, annual_price=int(annual_price))
