# TODO: at some point, move to peewee-async for theoretical, probably completely insignificant performance gains
#  https://peewee-async.readthedocs.io/en/latest/
from datetime import date

from peewee import *

import config

db = SqliteDatabase(config.DATABASE_URL, pragmas={'foreign_keys': 1})


class User(Model):
    discord_id = BigIntegerField()

    class Meta:
        database = db


class Thread(Model):
    author = ForeignKeyField(User, backref='threads')
    discord_guild = BigIntegerField()
    created = DateField()
    subject = TextField()
    content = TextField()

    class Meta:
        database = db


class Comment(Model):
    author = ForeignKeyField(User, backref='comments')
    thread = ForeignKeyField(Thread, backref='comments')
    created = DateField()
    content = TextField()

    class Meta:
        database = db


def initialize():
    """
    Connects to the database.
    """
    db.connect()
    db.create_tables([Thread, User, Comment])


def add_sample_data():
    user1 = User.create(discord_id=101)
    user2 = User.create(discord_id=69)
    thread1 = Thread.create(author=user1, created=date(1960, 1, 15),
                            discord_guild=101, subject="hello world", content="hi")
    Comment.create(author=user2, created=date(1969, 2, 12), thread=thread1, content="suh dude")
