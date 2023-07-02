import textwrap
import crown_utilities
import db
import dataclasses as data
import messages as m
import numpy as np
import unique_traits as ut
import help_commands as h
import uuid
import asyncio
import random
from .classes.custom_paginator import CustomPaginator
from .classes.arm_class import Arm
from .classes.card_class import Card
from .classes.title_class import Title
from .classes.player_class import Player
from .classes.battle_class import Battle
from .classes.summon_class import Summon
from cogs.battle_config import BattleConfig
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class Explore(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Explore Cog is ready!')


    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    @slash_command(description="Toggle Explore Mode On/Off or explore a universe", options=[
        SlashCommandOption(
            name="universe",
            description="Type universe you want to explore, or type 'all' to explore all universes",
            type=OptionType.STRING,
            required=False
        )
    ])
    async def explore(self, ctx: InteractionContext, universe=None):
        try:
            player = db.queryUser({"DID": str(ctx.author.id)})
            p = Player(player['AUTOSAVE'],
                player['DISNAME'], player['DID'], player['AVATAR'], player['GUILD'], player['TEAM'], player['FAMILY'],
                player['TITLE'], player['CARD'], player['ARM'], player['PET'], player['TALISMAN'], player['CROWN_TALES'],
                player['DUNGEONS'], player['BOSS_WINS'], player['RIFT'], player['REBIRTH'], player['LEVEL'],
                player['EXPLORE'], player['SAVE_SPOT'], player['PERFORMANCE'], player['TRADING'], player['BOSS_FOUGHT'],
                player['DIFFICULTY'], player['STORAGE_TYPE'], player['USED_CODES'], player['BATTLE_HISTORY'], player['PVP_WINS'],
                player['PVP_LOSS'], player['RETRIES'], player['PRESTIGE'], player['PATRON'], player['FAMILY_PET'],
                player['EXPLORE_LOCATION'], player['SCENARIO_HISTORY']
            )
            message = None
            if p.explore == 0:
                db.updateUserNoFilter({'DID': str(p.did)}, {'$set': {'EXPLORE': True}})
                message = f":milky_way: | Entering Explore Mode"
            elif p.explore == 1:
                db.updateUserNoFilter({'DID': str(p.did)}, {'$set': {'EXPLORE': False, 'EXPLORE_LOCATION': "NULL"}})
                message = ":rotating_light: | Exiting Explore Mode"

            if universe is not None:
                message = p.set_explore(universe)

            if message is not None:
                await ctx.send(f"{message}")

        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))


    @slash_command(description="Set Explore Channel")
    async def setexplorechannel(self, ctx: InteractionContext):
        if ctx.author.guild_permissions.administrator:
            guild = ctx.guild
            server_channel = ctx.channel
            server_query = {'GNAME': str(guild), 'EXP_CHANNEL': str(server_channel)}
            try:
                response = db.queryServer({'GNAME': str(guild)})
                if response:
                    update_channel = db.updateServer({'GNAME': str(guild)}, {'$set': {'EXP_CHANNEL': str(server_channel)}})
                    await ctx.send(f"Explore Channel updated to **{server_channel}**")
                    return
                else:
                    update_channel = db.createServer(data.newServer(server_query))
                    await ctx.send("Explore Channel set.")
                    return
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
        else:
            await ctx.send("Admin command only.")
            return


    @slash_command(description="Create Default Server Explore Channel")
    async def createexplorechannel(self, ctx: InteractionContext):
        guild = ctx.guild
        categoryname = "Explore"
        channelname = "explore-encounters"
        try:
            if ctx.author.guild_permissions.administrator == True:
                category = discord.utils.get(guild.categories, name=categoryname)
                if category is None: #If there's no category matching with the `name`
                    category = await guild.create_category_channel(categoryname)
                    setchannel = await guild.create_text_channel(channelname, category=category)
                    await ctx.send(f"New **Explore** Category and **{channelname}** Channel Created!")
                    await setchannel.send("**Explore Channel Set**")
                    return setchannel

                else: #Else if it found the categoty
                    setchannel = discord.utils.get(guild.text_channels, name=channelname)
                    if channel is None:
                        setchannel = await guild.create_text_channel(channelname, category=category)
                        await ctx.send(f"New Explore Channel is **{channelname}**")
                        await setchannel.send("**Explore Channel Set**")
                    else:
                        await ctx.send(f"Explore Channel Already Exist **{channelname}**")
                        await setchannel.send(f"{ctx.author.mention} Explore Here")            
                
            # else:
            #     print("Not Admin")
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
    


def setup(bot):
    Explore(bot)
              