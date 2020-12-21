from discord import Message
from discord.ext import commands
from configparser import ConfigParser
from os import path
# TODO: at some point, move to peewee-async for theoretical, probably completely insignificant performance gains
#  https://peewee-async.readthedocs.io/en/latest/
from peewee import *
from datetime import date

# root project directory
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
    author = CharField()  # TODO: add actual author model and link to it here
    created = DateField()

    class Meta:
        database = db


db.connect()
db.create_tables([Thread])
Thread.create(author='Joe', created=date(1960, 1, 15))

# print out all the threads we have in the database
for thread in Thread.select():
    print(f'{thread.created} {thread.author}')

CHANNEL = "support-channel"
if __name__ == '__main__':
    bot = commands.Bot(command_prefix='>')


    @bot.event
    async def on_message(message: Message):
        if message.channel.name == CHANNEL:
            print(f'Message sent in support channel: {message.content} from {message.author.name}')


    bot.run(API_KEY)
