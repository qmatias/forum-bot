from discord import Message
from discord.ext import commands
from configparser import ConfigParser
from os import path
from discord.ext.commands import Context

# TODO: at some point, move to peewee-async for theoretical, probably completely insignificant performance gains
#  https://peewee-async.readthedocs.io/en/latest/
from peewee import *
from datetime import date

# root project directory
ROOT_DIR = path.dirname(path.abspath(__file__))

CONFIG = ConfigParser()
try:
    CONFIG.read(path.join(ROOT_DIR, 'config.ini'))
    API_KEY = CONFIG['discord']['token']
    DATABASE_FILE = CONFIG['database']['url']
except Exception:
    raise IOError('Error reading config file')
db = SqliteDatabase(DATABASE_FILE, pragmas={'foreign_keys': 1})


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


db.connect()
db.create_tables([Thread, User, Comment])
myUser1 = User.create(discord_id=101)
myUser2 = User.create(discord_id=69)
thread1 = Thread.create(author=myUser1, created=date(1960, 1, 15), discord_guild=101, subject="hello world",
                        content="hi")
Comment.create(author=myUser2, created=date(1969, 2, 12), thread=thread1, content="suh dude")

# print out all the threads we have in the database
for thread in Thread.select():
    print(f'{thread.created} {thread.author.discord_id} {thread.content}')

CHANNEL = "support-channel"
if __name__ == '__main__':
    bot = commands.Bot(command_prefix='!')

    def is_support_channel():
        def _is_support_channel(ctx):
            return ctx.channel.name == CHANNEL
        return commands.check(_is_support_channel)

    @bot.command()
    @is_support_channel()
    async def ping(ctx: Context):
        msg = ""
        for thread in Thread.select():
            msg += f'{thread.created} {thread.author.discord_id} {thread.content} {thread.subject}\n'
        await ctx.send(msg)

    @bot.event
    async def on_command_error(ctx: Context, error: commands.CommandError):
        print(error)

    bot.run(API_KEY)
