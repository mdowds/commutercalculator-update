import peewee

from config import load_config_value


class CCModel(peewee.Model):
    class Meta:
        database = peewee.SqliteDatabase(load_config_value('dbFilePath'))
