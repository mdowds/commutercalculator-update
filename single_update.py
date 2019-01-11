import os

from google.cloud import firestore

from interfaces.database import Database
from models import Station
from updaters import JourneyTimesInteractor
from updaters.journey_costs_interactor import JourneyCostsInteractor

if __name__ == '__main__':
    firestore = firestore.Client()
    database = Database(firestore)
    chx = Station.from_dict(firestore.collection('destinations').document('CHX').get().to_dict())
    lew = Station.from_dict(firestore.collection('stations').document('LEW').get().to_dict())

    time_interactor = JourneyTimesInteractor(db=database, api_key=os.environ['GMAPS_API_KEY'])
    time = time_interactor.get_update(chx, lew)
    time_interactor.save_update(chx, lew, time.value)

    costs_interactor = JourneyCostsInteractor(db=database)
    costs = costs_interactor.get_update(chx, lew)
    costs_interactor.save_update(chx, lew, costs.value)

    print("Updated Lewisham to Charing Cross")
