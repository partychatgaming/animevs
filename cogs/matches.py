from collections import Counter
from interactions import listen, Extension
from logger import loggy

emojis = ['👍', '👎']

class Matches(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        #print('Matches Cog is ready!')
        loggy.info('Matches Cog is ready')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    # @slash_command(description="Analysis on Card")
    # async def analysis(self, ctx : InteractionContext, card: str):
    #     try:
    #         card_info = db.queryCard({'NAME': {"$regex": f"^{str(card)}$", "$options": "i"}})
    #         c = Card(card_info['NAME'], card_info['PATH'], card_info['PRICE'], card_info['EXCLUSIVE'], card_info['AVAILABLE'], card_info['IS_SKIN'], card_info['SKIN_FOR'], card_info['HLT'], card_info['HLT'], card_info['STAM'], card_info['STAM'], card_info['MOVESET'], card_info['ATK'], card_info['DEF'], card_info['TYPE'], card_info['PASS'][0], card_info['SPD'], card_info['UNIVERSE'], card_info['HAS_COLLECTION'], card_info['TIER'], card_info['COLLECTION'], card_info['WEAKNESS'], card_info['RESISTANT'], card_info['REPEL'], card_info['ABSORB'], card_info['IMMUNE'], card_info['GIF'], card_info['FPATH'], card_info['RNAME'], card_info['RPATH'], False)
    #         c.set_affinity_message()
    #         title = {'TITLE': 'CARD ANALYSIS'}
    #         arm = {'ARM': 'CARD ANALYSIS'}
    #         c.set_price_message_and_card_icon()
            
    #         match_query = {"CARD": str(card_info['NAME'])}
    #         response = db.queryManyMatches(match_query)
    #         if response:
    #             #card = db.queryCard({"NAME": card_info['NAME']})
    #             path = card_info['PATH']
    #             title_tales_matches = []
    #             title_dungeon_matches = []
    #             title_boss_matches = []
    #             title_pvp_matches = []
    #             universe_tales_matches = []
    #             universe_dungeon_matches = []
    #             arm_tales_matches = []
    #             arm_dungeon_matches = []
    #             arm_boss_matches = []
    #             arm_pvp_matches = []
    #             most_played = []

    #             for matches in response:
    #                 most_played.append(matches['PLAYER'])
    #                 if matches['UNIVERSE_TYPE'] == "Tales":
    #                     title_tales_matches.append(matches['TITLE'])
    #                     arm_tales_matches.append(matches['ARM'])
    #                     universe_tales_matches.append(matches['UNIVERSE'])
    #                 if matches['UNIVERSE_TYPE'] == "Dungeon":
    #                     title_dungeon_matches.append(matches['TITLE'])
    #                     arm_dungeon_matches.append(matches['ARM'])
    #                     universe_dungeon_matches.append(matches['UNIVERSE'])
    #                 if matches['UNIVERSE_TYPE'] == "Boss":
    #                     title_boss_matches.append(matches['TITLE'])
    #                     arm_boss_matches.append(matches['ARM'])
    #                 if matches['UNIVERSE_TYPE'] == "PVP":
    #                     title_pvp_matches.append(matches['TITLE'])
    #                     arm_pvp_matches.append(matches['ARM'])
                
    #             card_main = most_frequent(most_played)

    #             if title_tales_matches and arm_tales_matches:
    #                 tale_title = most_frequent(title_tales_matches)
    #                 tale_arm = most_frequent(arm_tales_matches)
    #                 tale_universe = most_frequent(universe_tales_matches)
    #                 tale_message = textwrap.dedent(f"""\
    #                 _Most Used Title:_ **{tale_title}**
    #                 _Most Used Arm:_ **{tale_arm}**
    #                 _Most Played Universe:_ **{tale_universe}**
    #                 """)
    #             else:
    #                 tale_message = textwrap.dedent(f"""\
    #                 _Not enough data for analysis_
    #                 """)

    #             if title_dungeon_matches and arm_dungeon_matches:
    #                 dungeon_title = most_frequent(title_dungeon_matches)
    #                 dungeon_arm = most_frequent(arm_dungeon_matches)
    #                 dungeon_universe = most_frequent(universe_dungeon_matches)
    #                 dungeon_message = textwrap.dedent(f"""\
    #                 _Most Used Title:_ **{dungeon_title}**
    #                 _Most Used Arm:_ **{dungeon_arm}**
    #                 _Most Played Universe:_ **{dungeon_universe}**
    #                 """)
    #             else:
    #                 dungeon_message = textwrap.dedent(f"""\
    #                 _Not enough data for analysis_
    #                 """)

    #             if title_boss_matches and arm_boss_matches:
    #                 boss_title = most_frequent(title_boss_matches)
    #                 boss_arm = most_frequent(arm_boss_matches)
    #                 boss_message = textwrap.dedent(f"""\
    #                 _Most Used Title:_ **{boss_title}**
    #                 _Most Used Arm:_ **{boss_arm}**
    #                 """)
    #             else:
    #                 boss_message = textwrap.dedent(f"""\
    #                 _Not enough data for analysis_
    #                 """)

    #             if title_pvp_matches and arm_pvp_matches:
    #                 pvp_title = most_frequent(title_pvp_matches)
    #                 pvp_arm = most_frequent(arm_pvp_matches)
    #                 pvp_message = textwrap.dedent(f"""\
    #                 _Most Used Title:_ **{pvp_title}**
    #                 _Most Used Arm:_ **{pvp_arm}**
    #                 """)
    #             else:
    #                 pvp_message = textwrap.dedent(f"""\
    #                 _Not enough data for analysis_
    #                 """)

    #             title = {'TITLE': 'CARD PREVIEW'}
    #             arm = {'ARM': 'CARD PREVIEW'}
                
                
    #             embedVar2 = Embed(title=f"🆚 {card_info['NAME']} | _Crown Analysis_".format(self), description=f"**Card Master**\n{card_main}", color=0xe91e63) 
    #             embedVar2.add_field(name=f":crown:Tales Stats", value=f"{tale_message}", inline=False)
    #             embedVar2.add_field(name=f"👺Dungeon Stats", value=f"{dungeon_message}", inline=False)
    #             embedVar2.add_field(name=f"👹Boss Stats", value=f"{boss_message}", inline=False)
    #             embedVar2.add_field(name=f"⚔️PVP Stats", value=f"{pvp_message}", inline=False)
    #             embedVar2.set_footer(text=f"/player {card_main} - Lookup Card Master")
    #             await ctx.send(embed=embedVar2, file=c.showcard())
                
                
    #         else:
    #             await ctx.send("Not enough data for analysis")
    #             return
    #     except Exception as ex:
    #         trace = []
    #         tb = ex.__traceback__
    #         while tb is not None:
    #             trace.append({
    #                 "filename": tb.tb_frame.f_code.co_filename,
    #                 "name": tb.tb_frame.f_code.co_name,
    #                 "lineno": tb.tb_lineno
    #             })
    #             tb = tb.tb_next
    #         print(str({
    #             'player': str(player),
    #             'type': type(ex).__name__,
    #             'message': str(ex),
    #             'trace': trace
    #         }))

def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]

def setup(bot):
    Matches(bot)