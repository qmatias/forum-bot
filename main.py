import discord
from discord.ext import commands
from configparser import ConfigParser
from os import path
from peewee import *
from datetime import date


# Root project directory
ROOT_DIR = path.dirname(path.abspath(__file__))

CONFIG = ConfigParser()
try:
    CONFIG.read(path.join(ROOT_DIR, 'config.ini'))
    API_KEY = CONFIG['main']['token']
    DATABASE_FILE = CONFIG['main']['databaseurl']
except Exception:
    raise IOError('Error reading config file')
db = SqliteDatabase(DATABASE_FILE)

class Thread(Model):
    author = CharField() # TODO: add actual author model
    created = DateField()

    class Meta:
        database = db

db.connect()
db.create_tables([Thread])
uncle_bob = Thread.create(author='hi', created=date(1960, 1, 15))

for person in Thread.select():
    print(person.author)


if __name__ == '__main__':
    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('weewee')

    @bot.event
    async def on_ready():
        print("hello")
        for guild in bot.guilds:
            print(guild.name)

    @bot.event
    async def on_message(message):
        if message.channel.name == "support-channel":
            print(message.channel)
        else:
            return

    bot.run(API_KEY)
