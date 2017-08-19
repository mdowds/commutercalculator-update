from peewee import ForeignKeyField, CharField, IntegerField
from .station import Station
from .cc_model import CCModel


class SeasonTicket(CCModel):
    destination = ForeignKeyField(Station)
    origin = CharField()
    annual_price = IntegerField()
