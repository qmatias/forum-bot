from datetime import datetime, timezone
from typing import Union

import discord
from discord import Colour, Embed, CategoryChannel, Reaction, User, TextChannel, Member
from discord.ext import commands
from database import Message
import sys
import config
import database

bot = commands.Bot(command_prefix='!')


def menu_channel():
    """
    A decorator to check if the command is being run from within :const:`config.CHANNEL`
    """
    def predicate(ctx):
        return ctx.channel.name == config.THREAD_CHANNEL

    return commands.check(predicate)


@bot.command()
@menu_channel()
async def new(ctx: commands.Context, *args):
    # delete the message
    await ctx.message.delete()

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
    thread_channel = await category.create_text_channel(thread_title,
                                                        overwrites=permissions)

    # create the embed message for the thread
    embed = Embed(
        title=config.EMBED_TITLE.format(title=thread_title),
        description=config.EMBED_DESCRIPTION.format(author=ctx.author.mention),
        color=config.EMBED_COLOR,
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
    thread_channel_id = Message.get(
        Message.message_id == event.message_id).channel_id
    thread_channel = bot.get_channel(thread_channel_id)

    # remove the yes/no reaction
    react_channel: TextChannel = bot.get_channel(event.channel_id)
    message = await react_channel.fetch_message(event.message_id)
    user = bot.get_user(event.user_id)
    await message.remove_reaction(event.emoji, user)

    # toggle read permissions for the user who reacted
    await thread_channel.set_permissions(user, overwrite=permissions)


@bot.event
async def on_command_error(ctx: commands.Context,
                           error: commands.CommandError):
    print(
        error, file=sys.stderr
    )  # print out the error message to standard error (make the text red in pycharm)


if __name__ == '__main__':
    database.initialize()
    bot.run(config.API_KEY)
