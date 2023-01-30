from re import T
import discord
from discord.ext import commands
import bot as main
import db
import dataclasses as data
import messages as m
import numpy as np
import help_commands as h
import unique_traits as ut
import crown_utilities
# Converters
from discord import User
from discord import Member
from PIL import Image, ImageFont, ImageDraw
import requests
from collections import ChainMap
import DiscordUtils
import random
import textwrap
from collections import Counter
from discord_slash import cog_ext, SlashContext

emojis = ['👍', '👎']

class Matches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Matches Cog is ready!')

    async def cog_check(self, ctx):
        return await main.validate_user(ctx)

    @cog_ext.cog_slash(description="Analysis on Card", guild_ids=main.guild_ids)
    async def analysis(self, ctx, card: str):
        try:
            card_info = db.queryCard({'NAME': {"$regex": f"^{str(card)}$", "$options": "i"}})
            match_query = {"CARD": str(card_info['NAME'])}
            response = db.queryManyMatches(match_query)
            if response:
                #card = db.queryCard({"NAME": card_info['NAME']})
                path = card_info['PATH']
                title_tales_matches = []
                title_dungeon_matches = []
                title_boss_matches = []
                title_pvp_matches = []
                universe_tales_matches = []
                universe_dungeon_matches = []
                arm_tales_matches = []
                arm_dungeon_matches = []
                arm_boss_matches = []
                arm_pvp_matches = []
                most_played = []

                for matches in response:
                    most_played.append(matches['PLAYER'])
                    if matches['UNIVERSE_TYPE'] == "Tales":
                        title_tales_matches.append(matches['TITLE'])
                        arm_tales_matches.append(matches['ARM'])
                        universe_tales_matches.append(matches['UNIVERSE'])
                    if matches['UNIVERSE_TYPE'] == "Dungeon":
                        title_dungeon_matches.append(matches['TITLE'])
                        arm_dungeon_matches.append(matches['ARM'])
                        universe_dungeon_matches.append(matches['UNIVERSE'])
                    if matches['UNIVERSE_TYPE'] == "Boss":
                        title_boss_matches.append(matches['TITLE'])
                        arm_boss_matches.append(matches['ARM'])
                    if matches['UNIVERSE_TYPE'] == "PVP":
                        title_pvp_matches.append(matches['TITLE'])
                        arm_pvp_matches.append(matches['ARM'])
                
                card_main = most_frequent(most_played)

                if title_tales_matches and arm_tales_matches:
                    tale_title = most_frequent(title_tales_matches)
                    tale_arm = most_frequent(arm_tales_matches)
                    tale_universe = most_frequent(universe_tales_matches)
                    tale_message = textwrap.dedent(f"""\
                    _Most Used Title:_ **{tale_title}**
                    _Most Used Arm:_ **{tale_arm}**
                    _Most Played Universe:_ **{tale_universe}**
                    """)
                else:
                    tale_message = textwrap.dedent(f"""\
                    _Not enough data for analysis_
                    """)

                if title_dungeon_matches and arm_dungeon_matches:
                    dungeon_title = most_frequent(title_dungeon_matches)
                    dungeon_arm = most_frequent(arm_dungeon_matches)
                    dungeon_universe = most_frequent(universe_dungeon_matches)
                    dungeon_message = textwrap.dedent(f"""\
                    _Most Used Title:_ **{dungeon_title}**
                    _Most Used Arm:_ **{dungeon_arm}**
                    _Most Played Universe:_ **{dungeon_universe}**
                    """)
                else:
                    dungeon_message = textwrap.dedent(f"""\
                    _Not enough data for analysis_
                    """)

                if title_boss_matches and arm_boss_matches:
                    boss_title = most_frequent(title_boss_matches)
                    boss_arm = most_frequent(arm_boss_matches)
                    boss_message = textwrap.dedent(f"""\
                    _Most Used Title:_ **{boss_title}**
                    _Most Used Arm:_ **{boss_arm}**
                    """)
                else:
                    boss_message = textwrap.dedent(f"""\
                    _Not enough data for analysis_
                    """)

                if title_pvp_matches and arm_pvp_matches:
                    pvp_title = most_frequent(title_pvp_matches)
                    pvp_arm = most_frequent(arm_pvp_matches)
                    pvp_message = textwrap.dedent(f"""\
                    _Most Used Title:_ **{pvp_title}**
                    _Most Used Arm:_ **{pvp_arm}**
                    """)
                else:
                    pvp_message = textwrap.dedent(f"""\
                    _Not enough data for analysis_
                    """)
                
                o_card = card_info['NAME']
                o_card_path = card_info['PATH']
                o_price = card_info['PRICE']
                o_exclusive = card_info['EXCLUSIVE']
                o_available = card_info['AVAILABLE']
                o_is_skin = card_info['IS_SKIN']
                o_skin_for = card_info['SKIN_FOR']
                o_max_health = card_info['HLT']
                o_health = card_info['HLT']
                o_stamina = card_info['STAM']
                o_max_stamina = card_info['STAM']
                o_moveset = card_info['MOVESET']
                o_attack = card_info['ATK']
                o_defense = card_info['DEF']
                o_type = card_info['TYPE']
                o_passive = card_info['PASS'][0]
                affinity_message = crown_utilities.set_affinities(card_info)
                o_speed = card_info['SPD']
                o_show = card_info['UNIVERSE']
                o_has_collection = card_info['HAS_COLLECTION']
                o_tier = card_info['TIER']
                traits = ut.traits
                show_img = db.queryUniverse({'TITLE': o_show})['PATH']
                o_collection = card_info['COLLECTION']
                resolved = False
                focused = False
                dungeon = False
                title = {'TITLE': 'CARD PREVIEW'}
                arm = {'ARM': 'CARD PREVIEW'}
                
                o_1 = o_moveset[0]
                o_2 = o_moveset[1]
                o_3 = o_moveset[2]
                o_enhancer = o_moveset[3]

                # Move 1
                move1 = list(o_1.keys())[0]
                move1ap = list(o_1.values())[0]
                move1_stamina = list(o_1.values())[1]
                move1_element = list(o_1.values())[2]
                move1_emoji = crown_utilities.set_emoji(move1_element)

                # Move 2
                move2 = list(o_2.keys())[0]
                move2ap = list(o_2.values())[0]
                move2_stamina = list(o_2.values())[1]
                move2_element = list(o_2.values())[2]
                move2_emoji = crown_utilities.set_emoji(move2_element)

                # Move 3
                move3 = list(o_3.keys())[0]
                move3ap = list(o_3.values())[0]
                move3_stamina = list(o_3.values())[1]
                move3_element = list(o_3.values())[2]
                move3_emoji = crown_utilities.set_emoji(move3_element)

                # Move Enhancer
                move4 = list(o_enhancer.keys())[0]
                move4ap = list(o_enhancer.values())[0]
                move4_stamina = list(o_enhancer.values())[1]
                move4enh = list(o_enhancer.values())[2]
                active_pet = {}
                pet_ability_power = 0
                card_exp = 150
                
                turn = 300
                    
                    
                card_file = showcard("non-battle", card_info, "none", o_max_health, o_health, o_max_stamina, o_stamina, resolved, title, focused,
                                o_attack, o_defense, turn, move1ap, move2ap, move3ap, move4ap, move4enh, 0, None)
                
                embedVar2 = discord.Embed(title=f":vs: {card_info['NAME']} | _Crown Analysis_".format(self), description=f"**Card Master**\n{card_main}", colour=0xe91e63) 
                embedVar2.add_field(name=f":crown:Tales Stats", value=f"{tale_message}", inline=False)
                embedVar2.add_field(name=f":fire:Dungeon Stats", value=f"{dungeon_message}", inline=False)
                embedVar2.add_field(name=f"👹Boss Stats", value=f"{boss_message}", inline=False)
                embedVar2.add_field(name=f"⚔️PVP Stats", value=f"{pvp_message}", inline=False)
                embedVar2.set_footer(text=f"/player {card_main} - Lookup Card Master")
                await ctx.send(embed=embedVar2, file=card_file)
                
                
            else:
                await ctx.send("Not enough data for analysis")
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
                'player': str(player),
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))

def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]

def setup(bot):
    bot.add_cog(Matches(bot))