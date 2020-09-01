import discord
from discord.ext import commands
from configparser import ConfigParser
from os import path

# Root project directory
ROOT_DIR = path.dirname(path.abspath(__file__))

CONFIG = ConfigParser()
try:
    CONFIG.read(path.join(ROOT_DIR, 'config.ini'))
    API_KEY = CONFIG['main']['token']
except Exception:
    raise IOError('Error reading config file')

if __name__ == '__main__':
    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run(API_KEY)
