from typing import Dict, Any


class Station:
    def __init__(self, sid: str, name: str, lat: float, long: float):
        self.sid = sid
        self.name = name
        self.lat = lat
        self.long = long

    @staticmethod
    def from_dict(dict: Dict[str, Any]) -> 'Station':
        return Station(
            sid=dict['sid'],
            name=dict['name'],
            lat=dict['location'].latitude,
            long=dict['location'].longitude
        )
