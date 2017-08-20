from typing import Dict, Optional
from fnplus import Either, tfilter

import requests

from models import Station


def get_season_ticket_annual_price(destination: Station, origin: Station) -> Either[int]:
    response = Either.fromfunction(_make_request, origin.sid, destination.sid)
    return response.call(_extract_weekly_fare).call(_calculate_annual_fare)


def _make_request(orig_id: str, dest_id: str) -> Dict:
    try:
        return requests.get("http://api.brfares.com/querysimple", params={"orig": orig_id, "dest": dest_id}).json()
    except Exception as e:
        raise e


def _extract_weekly_fare(response: Dict) -> Optional[int]:
    weekly_season_standard = tfilter(lambda fare: fare['ticket']['code'] == '7DS', response['fares'])
    if len(weekly_season_standard) == 0:
        print("No ticket found for " + response['orig']['crs'] + " to " + response['dest']['crs'])
    return weekly_season_standard[0]['adult']['fare'] if len(weekly_season_standard) > 0 else None


def _calculate_annual_fare(weekly_fare: int) -> int:
    return int((weekly_fare * 40) / 100)
