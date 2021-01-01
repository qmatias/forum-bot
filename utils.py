from discord import Colour, Embed
from discord.ext import commands
import random
import config


def random_color():
    """A factory method that returns a :class:`Colour` with a random hue.
    .. note::
        The random algorithm works by choosing a colour with a random hue but
        with maxed out saturation and value.
    """
    return Colour.from_hsv(random.random(), 1, 1)


def menu_channel():
    """
    A decorator to check if the command is being run from within :const:`config.CHANNEL`
    """
    def predicate(ctx):
        try:
            return ctx.channel.name == config.THREAD_CHANNEL
        except Exception:
            return False

    return commands.check(predicate)