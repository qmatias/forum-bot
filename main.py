from datetime import datetime, timezone
from discord import Colour, Embed, CategoryChannel, Reaction, User
from discord.ext import commands
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

    thread_channel = await category.create_text_channel(thread_title)

    embed = Embed(title=f"Thread: {thread_title}", description=f"Created by: {ctx.author.mention}",
                  color=Colour.gold(),
                  timestamp=datetime.now(timezone.utc))
    embed.set_thumbnail(url=ctx.author.avatar_url_as(size=32))

    for channel in (thread_channel, ctx.channel):
        message = await channel.send(embed=embed)
        await message.add_reaction('✅')
        database.Message.create(message_id=message.id, channel_id=channel.id)


@bot.event
async def on_reaction_add(reaction: Reaction, user: User):
    print(reaction.emoji)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    print(error, file=sys.stderr)  # print out the error message to standard error (make the text red in pycharm)


if __name__ == '__main__':
    database.initialize()
    bot.run(config.API_KEY)
