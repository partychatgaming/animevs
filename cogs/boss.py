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
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension
import logging
from logger import loggy

class Boss(Extension):
    def __init__(self, bot):
        self.bot = bot



    @listen()
    async def on_ready(self):
        # print('Boss Cog is ready!')
        loggy.info('Boss Cog is ready')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)
    
    @slash_command(description="Reset Abyss Level and Exchange Boss Souls for Cards")
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
            prestigemark = int(100 - int(prestigebonus))
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
                            u = await self.bot.bot.fetch_user(str(ctx.author.id))
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
                            #     response = db.updateUserNoFilter(vault_query,{'$addToSet':{'CARDS': str(card_info['NAME'])}})
                            #     r = db.updateUserNoFilter(vault_query, update_query)
                            # owned_destinies = []
                            # for destiny in vault['DESTINY']:
                            #     owned_destinies.append(destiny['NAME'])
                            # for destiny in d.destiny:
                            #     if card_info['NAME'] in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                            #         db.updateUserNoFilter(vault_query,{'$addToSet':{'DESTINY': destiny}})
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


    def set_selectable_bosses(self, ctx, mode, player):
        _all_universes = db.queryAllUniverse()
        
        
        def get_bosses(universes):
            all_universes = []
            for universe in universes:
                if universe["TITLE"] in player.completed_dungeons:
                    all_universes.append(universe)
            if not all_universes:
                return None
            else:
                return all_universes
        all_universes = get_bosses(_all_universes)
        #print(all_universes)
        available_universes = []
        selected_universe = ""
        universe_menu = []
        universe_embed_list = []
        available_dungeons_list = "Sadly, you have no available dungeons at this time!\n🌍 To unlock a Universe Dungeon you must first complete the Universe Tale!"
        can_fight_boss = False
        can_fight_message = "🗝️ | Conquer A Dungeon to Gain a Boss Key"
        if player.boss_fought == False:
            can_fight_boss = True
            can_fight_message = "📿| Boss Talismans ignore all Affinities. Be Prepared"
        difficulty = player.difficulty
        prestige_slider = 0
        p_message = ""
        aicon = crown_utilities.prestige_icon(player.prestige)
        if player.prestige > 0:
            prestige_slider = ((((player.prestige + 1) * (10 + player.rebirth)) /100))
            p_percent = (prestige_slider * 100)
            p_message = f"*{aicon} x{round(p_percent)}%*"
        if player.completed_tales:
            l = []
            for universe in player.completed_tales:
                if universe != "":
                    l.append(universe)
            available_dungeons_list = "\n".join(l)
        
        
        if len(player.completed_dungeons) > 25:
            all_universes = random.sample(all_universes, min(len(all_universes), 25))
            #print(all_universes)
        if not all_universes:
            return False
        for universe in all_universes:
            if universe['TITLE'] in player.completed_dungeons:
                if universe != "":
                    if universe['GUILD'] != "PCG":
                        universe_crest_owner_message = f"{crown_utilities.crest_dict[universe['TITLE']]} **Crest Owned**: {universe['GUILD']}"
                    else: 
                        universe_crest_owner_message = f"{crown_utilities.crest_dict[universe['TITLE']]} *Crest Unclaimed*"
                    if universe['UNIVERSE_BOSS'] != "":
                        boss_info = db.queryBoss({"NAME": universe['UNIVERSE_BOSS']})
                        if boss_info:
                            if boss_info['NAME'] in player.boss_wins:
                                completed = crown_utilities.utility_emojis['ON']
                            else:
                                completed = crown_utilities.utility_emojis['OFF']
                            embedVar = Embed(title= f"{universe['TITLE']}", description=textwrap.dedent(f"""
                            {crown_utilities.crest_dict[universe['TITLE']]} **Boss**: :japanese_ogre: **{boss_info['NAME']}**
                            🎗️ **Boss Title**: {boss_info['TITLE']}
                            🦾 **Boss Arm**: {boss_info['ARM']}
                            🧬 **Boss Summon**: {boss_info['PET']}
                            
                            **Difficulty**: ⚙️ {difficulty.lower().capitalize()} {p_message}
                            **Soul Aquired**: {completed}
                            {universe_crest_owner_message}
                            """))
                            embedVar.set_image(url=boss_info['PATH'])
                            #embedVar.set_thumbnail(url=ctx.author.avatar_url)
                            embedVar.set_footer(text=f"{can_fight_message}")
                            universe_embed_list.append(embedVar)

        if not universe_embed_list:
            universe_embed_list = Embed(title= f"👹 There are no available Bosses at this time.", description=textwrap.dedent(f"""
            \n__How to unlock Bosses?__
            \nYou unlock Bosses by completing the Universe Dungeon. Once a Dungeon has been completed the boss for that universe will be unlocked for you to fight!
            \n🗝️ | A Boss Key is required to Enter the Boss Arena.
            \nEarn Boss Keys by completing any Universe Dungeon.
            \n__🌍 Available Universe Dungeons__
            \n{available_dungeons_list}
            """))
            # embedVar.set_image(url=boss_info['PATH'])
            universe_embed_list.set_thumbnail(url=ctx.author.avatar_url)
            # embedVar.set_footer(text="Use /tutorial")


        return universe_embed_list




def setup(bot):
    Boss(bot)