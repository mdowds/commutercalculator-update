from typing import Dict
from fnplus import find, curried

import requests

from models import Station


@curried
def get_season_ticket_annual_price(destination: Station, origin: Station) -> int:
    response = _make_request(origin.sid, destination.sid)
    return _calculate_annual_fare(_extract_weekly_fare(response))


def _make_request(orig_id: str, dest_id: str) -> Dict:
    r = requests.get("http://api.brfares.com/querysimple", params={"orig": orig_id, "dest": dest_id})
    return r.json()


def _extract_weekly_fare(response: Dict) -> int:
    weekly_season_standard = find(lambda fare: fare['ticket']['code'] == '7DS', response['fares'])
    return weekly_season_standard['adult']['fare']


def _calculate_annual_fare(weekly_fare: int) -> int:
    return int((weekly_fare * 40) / 100)
