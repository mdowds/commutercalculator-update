import json
import os
import sys

from google.cloud import firestore
from google.oauth2 import service_account

import updaters
from interfaces.database import Database
from updaters import JourneyTimesInteractor
from updaters.journey_costs_interactor import JourneyCostsInteractor


def update_journey_times():

    key = json.loads(os.environ['GCLOUD_SA_KEY'])
    credentials = service_account.Credentials.from_service_account_info(key)

    database = Database(firestore.Client(project=os.environ['GCLOUD_PROJECT_ID'], credentials=credentials))
    interactor = JourneyTimesInteractor(db=database, api_key=os.environ['GMAPS_API_KEY'])

    update_results = updaters.update(interactor)
    print("Journey times: " + update_results.message)

    if update_results.has_errors:
        sys.exit(1)


def update_journey_costs():
    key = json.loads(os.environ['GCLOUD_SA_KEY'])
    credentials = service_account.Credentials.from_service_account_info(key)

    database = Database(firestore.Client(project=os.environ['GCLOUD_PROJECT_ID'], credentials=credentials))
    interactor = JourneyCostsInteractor(db=database)

    update_results = updaters.update(interactor)
    print("Journey costs: " + update_results.message)

    if update_results.has_errors:
        sys.exit(1)


if __name__ == '__main__':
    update_journey_times()
    update_journey_costs()
