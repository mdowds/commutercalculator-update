from datetime import datetime, date
from typing import Iterable

from fn.func import curried
from fn.iters import map
from google.cloud import firestore
from google.cloud.firestore_v1beta1 import DocumentSnapshot, DocumentReference, CollectionReference

from models import Station, JourneyCosts


class Database:
    def __init__(self, firestore: firestore.Client):
        self._firestore = firestore

    @property
    def _destinations(self) -> CollectionReference:
        return self._firestore.collection('destinations')

    @property
    def _stations(self) -> CollectionReference:
        return self._firestore.collection('stations')

    def get_stations_for_journey_time_update(self) -> Iterable[Station]:
        docs: Iterable[DocumentSnapshot] = self._destinations\
            .order_by('journey_times_updated')\
            .limit(1)\
            .get()

        return map(lambda doc: Station.from_dict(doc.to_dict()), docs)

    def get_stations_for_journey_costs_update(self) -> Iterable[Station]:
        this_year = date.today().year
        docs: Iterable[DocumentSnapshot] = self._destinations\
            .where('journey_costs_updated', '<', datetime(this_year, 1, 1))\
            .order_by('journey_costs_updated')\
            .limit(1).get()

        return map(lambda doc: Station.from_dict(doc.to_dict()), docs)

    def get_all_stations(self) -> Iterable[Station]:
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

    def save_journey_costs(self, destination: Station, origin: Station, costs: JourneyCosts):
        destination_ref: DocumentReference = self._firestore.collection('destinations').document(destination.sid)
        journey_ref: DocumentReference = destination_ref.collection('journeys').document(origin.sid)

        season_ticket = {'season_ticket': costs.season_ticket.to_dict()} \
            if costs.season_ticket is not None else {}

        if journey_ref.get().exists:
            return journey_ref.update({
                'travelcard': costs.travelcard.to_dict(),
                **season_ticket
            })
        else:
            return journey_ref.set({
                'origin': self._stations.document(origin.sid).get().to_dict(),
                'travelcard': costs.travelcard.to_dict(),
                **season_ticket
            })

    def update_journey_times_updated(self, destination: Station, timestamp: datetime):
        self._destinations.document(destination.sid).update({
            'journey_times_updated': timestamp
        })

    def update_journey_costs_updated(self, destination: Station, timestamp: datetime):
        self._destinations.document(destination.sid).update({
            'journey_costs_updated': timestamp
        })
