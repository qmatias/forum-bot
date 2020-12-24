from datetime import datetime, timezone

import discord
from discord import Colour, Embed, CategoryChannel, Reaction, User, TextChannel
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
    await ctx.message.delete()
    thread_title = ' '.join(args)  # gives you a string of all the arguments, joined by spaces
    for channel in ctx.guild.channels:
        if isinstance(channel, CategoryChannel) and channel.name == config.THREAD_CATEGORY:
            category = channel
            break
    else:
        category = await ctx.guild.create_category(config.THREAD_CATEGORY)

    # permissions for the new channel
    # no one can see the channel except whoever created the thread
    permissions = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True)
    }
    thread_channel = await category.create_text_channel(thread_title, overwrites=permissions)

    embed = Embed(title=f'Thread: {thread_title}', description=f'Created by: {ctx.author.mention}\n'
                                                               f'React with ✅ to open.\n'
                                                               f'React with ❌ to close.\n',
                  color=Colour.gold(),
                  timestamp=datetime.now(timezone.utc))
    embed.set_thumbnail(url=ctx.author.avatar_url_as(size=32))

    for channel in (thread_channel, ctx.channel):
        message = await channel.send(embed=embed)
        await message.add_reaction(config.REACTION_YES)
        await message.add_reaction(config.REACTION_NO)
        Message.create(message_id=message.id, channel_id=thread_channel.id)


@bot.event
async def on_reaction_add(reaction: Reaction, user: User):
    # make sure we don't act own our own reactions
    if reaction.me:
        return

    # get either YES reaction (check mark) or NO reaction (X)
    if reaction == config.REACTION_YES:
        toggle = True
    elif reaction == config.REACTION_NO:
        toggle = False
    else:
        return

    # get the channel from the database which corresponds to the reacted message
    channel_id = Message.get(Message.message_id == reaction.message.id).channel_id
    channel: TextChannel = reaction.message.guild.get_channel(channel_id)

    # toggle read permissions for the user who reacted
    await channel.set_permissions(user, read_messages=toggle)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    print(error, file=sys.stderr)  # print out the error message to standard error (make the text red in pycharm)


if __name__ == '__main__':
    database.initialize()
    bot.run(config.API_KEY)
