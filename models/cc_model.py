import peewee
import os


class CCModel(peewee.Model):
    class Meta:
        #TODO: Make path to DB configurable
        database = peewee.SqliteDatabase(os.path.join(os.getcwd(), 'data', 'ccdb.sqlite'))
