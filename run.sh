#!/bin/sh

python update_journey_times.py /app/data/ccdb.sqlite -k $GMAPS_API_KEY;
python update_season_tickets.py /app/data/ccdb.sqlite -k $GMAPS_API_KEY;
