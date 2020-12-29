from configparser import ConfigParser
from os import path
from discord import Colour

# root project directory
ROOT_DIR = path.dirname(path.abspath(__file__))

# read from config.ini configuration file
CONFIG = ConfigParser()
CONFIG.read(path.join(ROOT_DIR, 'config.ini'))
try:
    API_KEY = CONFIG['discord']['token']
    DATABASE_URL = CONFIG['database']['url']
except Exception:
    raise IOError('Error while reading config file')

# discord channel for threads to go into
THREAD_CHANNEL = 'support-channel'
THREAD_CATEGORY = 'threads'

# reactions
EMBED_DESCRIPTION = \
'''Created by: {author}
React with ✅ to open.
React with ❌ to close.'''
EMBED_COLOR = Colour.gold()
EMBED_TITLE = 'Thread: {title}'
REACTION_YES = '✅'
REACTION_NO = '❌'
