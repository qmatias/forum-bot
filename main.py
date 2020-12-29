from datetime import datetime, timezone

import discord
from discord import Colour, Embed, CategoryChannel, Reaction, User, TextChannel, Member
from discord.ext import commands
from database import Message
import sys
import peewee
import config
import database

from utils import random_color, CustomHelpCommand, menu_channel

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config.PREFIX),
                   help_command=CustomHelpCommand())


@bot.event
async def on_ready():
    # Setting `Listening ` status
    await bot.change_presence(activity=discord.Streaming(name="My Stream", url='https://m.twitch.tv/rogsterr/clip/ThankfulJollyBottleTheThing'
))



@bot.event
@menu_channel()
async def on_message(message: discord.Message):
    # make sure we don't delete our own messages
    if message.author == bot.user:
        return

    # delete the message
    await message.delete()

    # process other bot commands
    await bot.process_commands(message)


@bot.command(name='new',
             help='Create a new thread',
             usage='<title>',
             aliases=['create'])
@menu_channel()
async def new(ctx: commands.Context, *args):
    # gives you a string of all the arguments, joined by spaces
    thread_title = ' '.join(args)
    for channel in ctx.guild.channels:
        if isinstance(channel, CategoryChannel) \
                and channel.name == config.THREAD_CATEGORY:
            category = channel
            break
    else:
        category = await ctx.guild.create_category(config.THREAD_CATEGORY)

    # permissions for the new channel
    # no one can see the channel except whoever created the thread
    permissions = {
        ctx.guild.default_role:
        discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True)
    }
    try:
        thread_channel = await category.create_text_channel(
            thread_title, overwrites=permissions)
    except Exception:  # title is too long, invalid character, etc etc
        # TODO tell the user their title is too long
        return

    # create the embed message for the thread
    color = random_color()
    embed = Embed(
        title=config.EMBED_TITLE.format(title=thread_title),
        description=config.EMBED_DESCRIPTION.format(author=ctx.author.mention),
        color=color,
        timestamp=datetime.now(timezone.utc))
    embed.set_thumbnail(url=ctx.author.avatar_url_as(size=32))

    # send the embed in both the main listing channel `ctx.channel` and the new
    # channel we created for the thread `thread_channel`
    # then add the sent message to our database
    for channel in (thread_channel, ctx.channel):
        message = await channel.send(embed=embed)
        await message.add_reaction(config.REACTION_YES)
        await message.add_reaction(config.REACTION_NO)
        Message.create(message_id=message.id, channel_id=thread_channel.id)


@bot.event
async def on_raw_reaction_add(event: discord.RawReactionActionEvent):
    # make sure we don't act own our own reactions
    if event.user_id == bot.user.id:
        return

    # remove the yes/no reaction
    react_channel: TextChannel = bot.get_channel(event.channel_id)
    message = await react_channel.fetch_message(event.message_id)
    user = bot.get_user(event.user_id)
    await message.remove_reaction(event.emoji, user)

    # get either YES reaction (check mark) or NO reaction (X)
    if event.emoji.name == config.REACTION_YES:
        permissions = discord.PermissionOverwrite(
            read_messages=True
        )  # give full reading permissions on "yes" reaction
    elif event.emoji.name == config.REACTION_NO:
        permissions = None  # reset permissions on "no" reaction
    else:
        return

    # look up the corresponding thread in the database
    # if the message doesn't exist in the database we can just exit
    try:
        message_record: Message = Message.get(
            Message.message_id == event.message_id)
    except peewee.DoesNotExist:
        return

    # if channel doesn't exist, remove the record from the database too
    thread_channel = bot.get_channel(message_record.channel_id)
    if not thread_channel:
        # this is not strictly nessecary (invalid records in the database don't really do any harm)
        # but what's the point in keeping them?
        message_record.delete_instance()
        return

    # toggle read permissions for the user who reacted
    await thread_channel.set_permissions(user, overwrite=permissions)


# @bot.event
# async def on_command_error(ctx: commands.Context,
#                            error: commands.CommandError):
#     print(
#         error, file=sys.stderr
#     )  # print out the error message to standard error (make the text red in pycharm)

if __name__ == '__main__':
    database.initialize()
    bot.run(config.API_KEY)
