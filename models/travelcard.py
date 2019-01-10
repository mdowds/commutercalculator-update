from typing import Dict, Optional


class Travelcard:
    def __init__(self, min_zone: int, max_zone: int, annual_price: int) -> None:
        self.min_zone = min_zone
        self.max_zone = max_zone
        self.annual_price = annual_price

    def to_dict(self) -> Dict[str, int]:
        return {
            'min_zone': self.min_zone,
            'max_zone': self.max_zone,
            'annual_price': self.annual_price
        }

    @staticmethod
    def for_zones(min_zone: int, max_zone: int) -> Optional['Travelcard']:
        try:
            annual_price = prices[str(min_zone)][str(max_zone)]
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
        '9': 3660
    },
    '2': {
        '2': 1052,
        '3': 1052,
        '4': 1164,
        '5': 1396,
        '6': 1756,
        '7': 1824,
        '8': 2480,
        '9': 2480
    }
}
