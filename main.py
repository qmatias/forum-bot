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
async def ping(ctx: commands.Context):
    msg = ""
    for thread in database.Thread.select():
        msg += f'{thread.created} {thread.author.discord_id} {thread.content} {thread.subject}\n'
    await ctx.send(msg)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    print(error, file=sys.stderr)  # print out the error message to standard error (make the text red in pycharm)


if __name__ == '__main__':
    bot.run(config.API_KEY)
