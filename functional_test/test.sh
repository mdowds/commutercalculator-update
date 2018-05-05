#!/bin/bash

# Exit immediately on non-0 response
set -e

journey_result=`python update_journey_times.py /app/data/ccdb.sqlite --debug`
echo "$journey_result"

ticket_result=`python update_season_tickets.py /app/data/ccdb.sqlite --debug`
echo "$ticket_result"
