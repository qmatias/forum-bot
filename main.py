from datetime import datetime, timezone
from discord import Colour, Embed, CategoryChannel, Reaction, User
from discord.ext import commands
import sys
import config
import database

bot = commands.Bot(command_prefix='!')


def thread_channel():
    """
    A decorator to check if the command is being run from within :const:`config.CHANNEL`
    """

    def _thread_channel(ctx):
        return ctx.channel.name == config.THREAD_CHANNEL

    return commands.check(_thread_channel)


@bot.command()
@thread_channel()
async def new(ctx: commands.Context, *args):
    await ctx.message.delete()
    thread_title = ' '.join(args)  # gives you a string of all the arguments, joined by spaces
    for channel in ctx.guild.channels:
        if isinstance(channel, CategoryChannel) and channel.name == config.THREAD_CATEGORY:
            category = channel
            break
    else:
        category = await ctx.guild.create_category(config.THREAD_CATEGORY)

    channel = await category.create_text_channel(thread_title)

    menu_embed = Embed(title=f"Thread: {thread_title}", description=f"Created by: {ctx.author.mention}",
                       color=Colour.gold(),
                       timestamp=datetime.now(timezone.utc))
    menu_embed.set_thumbnail(url=ctx.author.avatar_url_as(size=32))
    thread_embed = menu_embed
    channel_msg = await channel.send(embed=menu_embed)
    menu_msg = await ctx.send(embed=thread_embed)
    await menu_msg.add_reaction('✅')
    await channel_msg.add_reaction('✅')
    database.Message.create(message_id=channel_msg.id, channel_id=channel.id)
    database.Message.create(message_id=menu_msg.id, channel_id=channel.id)


@bot.event
async def on_reaction_add(reaction: Reaction, user: User):
    print(reaction.emoji)

#@bot.event
#async def add_reaction():

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    print(error, file=sys.stderr)  # print out the error message to standard error (make the text red in pycharm)


if __name__ == '__main__':
    database.initialize()
    bot.run(config.API_KEY)
