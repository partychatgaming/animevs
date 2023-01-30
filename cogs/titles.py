import discord
from discord.ext import commands
import bot as main
import crown_utilities
import db
import dataclasses as data
import messages as m
import numpy as np
import help_commands as h
# Converters
from discord import User
from discord import Member
from PIL import Image, ImageFont, ImageDraw
import requests
from discord_slash import cog_ext, SlashContext
from discord_slash import SlashCommand
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

class Titles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_ready(self):
        print('Titles Cog is ready!')

    async def cog_check(self, ctx):
        return await main.validate_user(ctx)

    @cog_ext.cog_slash(description="Equip a Title", guild_ids=main.guild_ids)
    async def equiptitle(self, ctx, title: str):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        title_name = title
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)

        vault_query = {'DID' : str(ctx.author.id)}
        vault = db.altQueryVault(vault_query)

        resp = db.queryTitle({'TITLE': {"$regex": f"^{str(title_name)}$", "$options": "i"}})
        title_name = resp['TITLE']

        if resp:

            if title_name in vault['TITLES']:
                response = db.updateUserNoFilter(user_query, {'$set': {'TITLE': title_name}})
                await ctx.send(f"**{title_name}** has been equipped.")
            else:
                await ctx.send(m.USER_DOESNT_HAVE_THE_Title, hidden=True)
        else:

            if title_name in vault['TITLES']:
                response = db.updateUserNoFilter(user_query, {'$set': {'TITLE': str(title_name)}})
                await ctx.send(f"**{title_name}** has been equipped.")
            else:
                await ctx.send(m.USER_DOESNT_HAVE_THE_Title, hidden=True)

def setup(bot):
    bot.add_cog(Titles(bot))
    
