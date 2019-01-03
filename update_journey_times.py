import os
import sys

from google.cloud import firestore

import updaters
from interfaces.database import Database
from updaters import JourneyTimesInteractor

if __name__ == '__main__':
    database = Database(firestore.Client())
    interactor = JourneyTimesInteractor(db=database, api_key=os.environ['GMAPS_API_KEY'])

    update_results = updaters.update(interactor)
    print("Journey times: " + update_results.message)

    if update_results.has_errors:
        sys.exit(1)
