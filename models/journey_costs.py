from typing import Dict, Optional, NamedTuple, Union


class Travelcard:
    def __init__(self, min_zone: str, max_zone: str, annual_price: int) -> None:
        self.min_zone = min_zone
        self.max_zone = max_zone
        self.annual_price = annual_price

    def to_dict(self) -> Dict[str, Union[int, str]]:
        return {
            'min_zone': self.min_zone,
            'max_zone': self.max_zone,
            'annual_price': self.annual_price
        }

    @staticmethod
    def for_zones(min_zone: str, max_zone: str) -> Optional['Travelcard']:
        try:
            annual_price = prices[min_zone][max_zone]
            return Travelcard(min_zone=min_zone, max_zone=max_zone, annual_price=annual_price)
        except KeyError:
            return None


prices = {
    '1': {
        '1': 1404,
        '2': 1404,
        '3': 1648,
        '4': 2020,
        '5': 2400,
        '6': 2568,
        '7': 2792,
        '8': 3300,
        '9': 3660,
        'WFJ': 3680,
        'SNF': 4364
    },
    '2': {
        '2': 1052,
        '3': 1052,
        '4': 1164,
        '5': 1396,
        '6': 1756,
        '7': 1824,
        '8': 2480,
        '9': 2480,
        'WFJ': 2480,
        'SNF': 3312
    }
}


class SeasonTicket:
    def __init__(self, annual_price: int) -> None:
        self.annual_price = annual_price

    def to_dict(self) -> Dict[str, int]:
        return {
            'annual_price': self.annual_price
        }


JourneyCosts = NamedTuple('JourneyCosts', (('season_ticket', Optional[SeasonTicket]), ('travelcard', Travelcard)))
