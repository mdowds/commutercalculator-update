from typing import Any, Dict, List

from google.cloud.firestore import GeoPoint


def make_station_dict(sid: str,
                      name: str, 
                      location: GeoPoint = GeoPoint(0.0, 0.0),
                      zones: List[int] = [],
                      modes: str = "") -> Dict[str, Any]:
    return {
        'sid': sid,
        'name': name,
        'location': location,
        'zones': zones,
        'modes': modes
    }


def make_journey_dict(origin: Dict[str, Any]) -> Dict[str, Any]:
    return {
        origin['sid']: {
            'origin': origin
        }
    }
