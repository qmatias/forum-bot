# TODO: at some point, move to peewee-async for theoretical, probably completely insignificant performance gains
#  https://peewee-async.readthedocs.io/en/latest/
from datetime import date

from peewee import *

import config

db = SqliteDatabase(config.DATABASE_URL, pragmas={'foreign_keys': 1})


class Message(Model):
    message_id = BigIntegerField(primary_key=True)
    channel_id = BigIntegerField()

    class Meta:
        database = db


def initialize():
    """
    Connects to the database.
    """
    db.connect()
    db.create_tables([Message])
