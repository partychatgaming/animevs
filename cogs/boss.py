import textwrap
import discord
from discord.ext import commands
import bot as main
import db
import crown_utilities
import classes as data
import messages as m
import numpy as np
import help_commands as h
import unique_traits as ut
import destiny as d
# Converters
from discord import User
from discord import Member
from PIL import Image, ImageFont, ImageDraw
import requests
from discord_slash import cog_ext, SlashContext

class Boss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_ready(self):
        print('Boss Cog is ready!')

    async def cog_check(self, ctx):
        return await main.validate_user(ctx)
    
    @cog_ext.cog_slash(description="Reset Abyss Level and Exchange Boss Souls for Cards", guild_ids=main.guild_ids)
    async def exchange(self, ctx, boss : str, card : str):
        try:
            vault_query = {'DID' : str(ctx.author.id)}
            vault = db.queryVault(vault_query)
            owned_destinies = []
            for destiny in vault['DESTINY']:
                owned_destinies.append(destiny['NAME'])
            userinfo = db.queryUser({"DID" : str(ctx.author.id)})
            prestige = int(userinfo['PRESTIGE'])
            prestigebonus = int(prestige) * 10
            prestigemark = int(101 - int(prestigebonus))
            prestige = prestige + 1
            
            
            if userinfo['LEVEL'] < prestigemark:
                await ctx.send(f"🔓 Unlock **Soul Exchange** by completing **Floor {prestigemark}** of the 🌑 Abyss! Use /solo to enter the abyss.")
                return
            
            
            bossname = boss
            cardname = card
            boss_info = db.queryBoss({'NAME': {"$regex": str(bossname), "$options": "i"}})
            mintedBoss = ""
            if userinfo:
                soul_list = userinfo['BOSS_WINS']
                for souls in soul_list:
                    if bossname == souls:
                        mintedBoss = bossname
                if mintedBoss =="":
                    await ctx.send("You do not own this Boss Soul", delete_after=3)
                    return
                elif boss_info:
                    card_info = db.queryCard({'NAME': {"$regex": str(cardname), "$options": "i"}})
                    if card_info:
                        uboss_name = boss_info['NAME']
                        uboss_show = boss_info['UNIVERSE']
                        card_show = card_info['UNIVERSE']
                        if uboss_show == card_show:
                            # if card_info['HAS_COLLECTION']:
                            #     await ctx.send(f"You can not use exchange on Destiny cards.")
                            #     return
                            response = await crown_utilities.store_drop_card(str(ctx.author.id), card_info['NAME'], card_show, vault, owned_destinies, 100000000, 100000000, "Ex", False, 0, "cards")
                            db.updateUserNoFilter({'DID' : str(ctx.author.id)}, {'$set' : {'LEVEL' : 0,}})
                            db.updateUserNoFilter({'DID' : str(ctx.author.id)}, {'$inc' : {'PRESTIGE' : 1}})
                            db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'BOSS_WINS': str(bossname)}})
                            await ctx.send(response)
                            await ctx.send(f"{ctx.author.mention} :japanese_ogre: **Soul Exchange** : You are now 🌑 **Abyss level** *0*! and :crown: **Prestige Level** {prestige}")
                            return response
                            # card_owned = False
                            
                            # for c in vault['CARD_LEVELS']:
                            #     if c['CARD'] == str(card_info['NAME']):
                            #         card_owned = True
                            # if not card_owned:
                            #     uni = db.queryUniverse({'TITLE': card_info['UNIVERSE']})
                            #     tier = uni['TIER']
                            #     update_query = {'$addToSet': {'CARD_LEVELS': {'CARD': str(card_info['NAME']), 'LVL': 0, 'TIER': int(tier), 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
                            #     response = db.updateVaultNoFilter(vault_query,{'$addToSet':{'CARDS': str(card_info['NAME'])}})
                            #     r = db.updateVaultNoFilter(vault_query, update_query)
                            # owned_destinies = []
                            # for destiny in vault['DESTINY']:
                            #     owned_destinies.append(destiny['NAME'])
                            # for destiny in d.destiny:
                            #     if card_info['NAME'] in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                            #         db.updateVaultNoFilter(vault_query,{'$addToSet':{'DESTINY': destiny}})
                            #         await ctx.send(f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault.")
                            db.updateUserNoFilter({'DID' : str(ctx.author.id)}, {'$set' : {'LEVEL' : 0,}})
                            db.updateUserNoFilter({'DID' : str(ctx.author.id)}, {'$inc' : {'PRESTIGE' : 1}})
                            db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'BOSS_WINS': str(bossname)}})
                            await ctx.send(response)
                            
                        else:
                            await ctx.send("Card must match Boss Universe", delete_after=3)
                        
                    else:
                        await ctx.send("Card Doesn't Exist", delete_after=3)
                else:
                    await ctx.send("Boss Doesn't Exist", delete_after=3)               
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
            await ctx.send(f"Error when exchanging boss soul. Alert support. Thank you!")
            return


def setup(bot):
    bot.add_cog(Boss(bot))