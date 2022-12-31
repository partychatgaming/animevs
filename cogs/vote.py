from itertools import filterfalse
import discord
from discord.ext import commands
import topgg
import bot as main
import db
import classes as data
import messages as m
import numpy as np
import help_commands as h
import textwrap
import DiscordUtils
import destiny as d
# Converters
from discord import User
from discord import Member
from PIL import Image, ImageFont, ImageDraw
import requests
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from dinteractions_Paginator import Paginator
import topgg

from discord.ext import commands

import dbl


class TopGG(commands.Cog):
    """
    This example uses dblpy's webhook system.
    In order to run the webhook, at least webhook_port must be specified (number between 1024 and 49151).
    """

    def __init__(self, bot):
        self.bot = bot
        
def setup(bot):
    bot.add_cog(TopGG(bot))