from peewee import Model, SqliteDatabase

from config import load_config_value


def _database_path() -> SqliteDatabase:
    try:
        return SqliteDatabase(load_config_value('dbFilePath'))
    except KeyError:
        return SqliteDatabase(':memory:')


class CCModel(Model):
    class Meta:
        database = _database_path()
