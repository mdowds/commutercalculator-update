from peewee import ForeignKeyField, CharField, IntegerField
from .station import Station
from .cc_model import CCModel


class JourneyTime(CCModel):
    origin = ForeignKeyField(Station)
    destination = CharField()
    time = IntegerField()
