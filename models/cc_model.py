from peewee import Model, SqliteDatabase

cc_database = SqliteDatabase(None)


class CCModel(Model):
    class Meta:
        database = cc_database
