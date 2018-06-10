import argparse
import os
import sys

import updaters
from models import cc_database
from updaters import JourneyTimesInteractor

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to the Sqlite database file', type=str)
    parser.add_argument('-k', '--key', help='Google Maps API key', type=str)
    parser.add_argument('-d', '--debug', action='store_true', help='run in debug mode')
    args = parser.parse_args()

    if not os.path.isfile(args.path):
        print("Error: file not found at " + args.path)
        sys.exit(2)

    cc_database.init(args.path)
    interactor = JourneyTimesInteractor(api_key=args.key, debug=args.debug)
    update_results = updaters.update(interactor)
    print("Journey times: " + update_results.message)

    if update_results.has_errors:
        sys.exit(1)
