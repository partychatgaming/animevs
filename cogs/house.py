import crown_utilities
import db
import dataclasses as data
import messages as m
import numpy as np
import help_commands as h
# Converters
from PIL import Image, ImageFont, ImageDraw
import requests
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension
import logging
from logger import loggy

class House(Extension):
    def __init__(self, bot):
        self.bot = bot



    @listen()
    async def on_ready(self):
        print('House Cog is ready!')
        loggy.info('House Cog is ready')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)


    # #@slash_command(description="Buy a House for your family")
    # async def buyhouse(self, ctx, house: str):
    #     registered_player = await crown_utilities.player_check(ctx)
    #     if not registered_player:
    #         return
    #     try: 
    #         house_name = house
    #         family_query = {'HEAD' : str(ctx.author)}
    #         family = db.queryFamily(family_query)
    #         house = db.queryHouse({'HOUSE': {"$regex": f"^{str(house)}$", "$options": "i"}})
    #         currentBalance = family['BANK']
    #         cost = house['PRICE']
    #         house_name = house['HOUSE']
    #         if house:
    #             if house_name in family['HOUSE']:
    #                 await ctx.send(m.USERS_ALREADY_HAS_HOUSE, delete_after=5)
    #             else:
    #                 newBalance = currentBalance - cost
    #                 if newBalance < 0 :
    #                     await ctx.send("You have an insufficent Balance")
    #                 else:
    #                     await crown_utilities.cursefamily(cost, family['HEAD'])
    #                     response = db.updateFamily(family_query,{'$set':{'HOUSE': str(house_name)}})
    #                     await ctx.send(m.PURCHASE_COMPLETE_H + "Enjoy your new Home!")
    #                     return
    #         else:
    #             await ctx.send(m.HOUSE_DOESNT_EXIST)
    #     except Exception as ex:
    #             trace = []
    #             tb = ex.__traceback__
    #             while tb is not None:
    #                 trace.append({
    #                     "filename": tb.tb_frame.f_code.co_filename,
    #                     "name": tb.tb_frame.f_code.co_name,
    #                     "lineno": tb.tb_lineno
    #                 })
    #                 tb = tb.tb_next
    #             print(str({
    #                 'type': type(ex).__name__,
    #                 'message': str(ex),
    #                 'trace': trace
    #             }))

def setup(bot):
    House(bot)