import os

from google.cloud import firestore

from interfaces.database import Database
from models import Station
from updaters import JourneyTimesInteractor

if __name__ == '__main__':
    firestore = firestore.Client()
    database = Database(firestore)
    interactor = JourneyTimesInteractor(db=database, api_key=os.environ['GMAPS_API_KEY'])

    bank = Station.from_dict(firestore.collection('destinations').document('BAH').get().to_dict())
    kgx = Station.from_dict(firestore.collection('destinations').document('KGX').get().to_dict())

    time = interactor.get_update(bank, kgx)
    interactor.save_update(bank, kgx, time.value)
    print("Updated Bank to King's Cross")
