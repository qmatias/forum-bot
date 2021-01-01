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

# discord command prefix
PREFIX = '!'

# discord channel for threads to go into
THREAD_CHANNEL = 'support-channel'
THREAD_CHANNEL_DESCRIPTION = f'Type {PREFIX}help for help with using the bot'
THREAD_CATEGORY = 'threads'

# reactions
REACTION_YES = '✅'
REACTION_NO = '❌'
EMBED_DESCRIPTION = \
f'''Created by: {{author}}
React with {REACTION_YES} to open.
React with {REACTION_NO} to close.'''
EMBED_TITLE = 'Thread: {title}'

# messages
INVALID_TITLE = '{author}: Please enter a title under 200 characters!'
INVALID_COMMAND = f'{{author}}: Please enter a valid command. Type {PREFIX}help for help.'
NO_PERMISSIONS = '{author}: The bot doesn\'t have permissions to do that.'
MESSAGE_TIMER = 15

# help
HELP_COLOR = Colour.blue()
HELP_TITLE = 'Help page {page}'
HELP_MESSAGE = \
f'''
{PREFIX}help: See this help message
{PREFIX}new <title>: Create a new thread
'''.strip()