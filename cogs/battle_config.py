import crown_utilities
import db
from cogs.play import Play as play
from cogs.classes.battle_class import Battle
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension
import logging
from logger import loggy

class BattleConfig(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.tutorial_basic = False
        self.tutorial_special = False
        self.tutorial_ultimate = False
        self.tutorial_block = False
        self.tutorial_focus = False
        self.tutorial_opponent_focus = False
        self.tutorial_resolve = False
        self.tutorialsummon = False
        self.tutorial_enhancer = False
        self.tutorial_talisman = False
        self.is_rpg = False
        
    @listen()
    async def on_ready(self):
        # print('BattleConfig Cog is ready!')
        loggy.info('BattleConfig Cog is ready')


    async def create_universe_battle(self, ctx, mode, universe, player, currentopponent, entrance_fee, coop_player=None):
        """
        crestlist, crestsearch are both in the player class
        Build the universe selection object that will go to battle.set_universe_selection_config
        Calls config_battle_players to build the player objects, then calls game.battle_commands to start the battle
        """

        if universe['TITLE'] in player.crestlist:
            await ctx.send(f"{crown_utilities.crest_dict[universe['TITLE']]} | 🎏 {player.association} {universe['TITLE']} Crest Activated! No entrance fee!")
        else:
            if int(player.balance) <= entrance_fee:
                await ctx.send(f"Tales require an 🪙 {'{:,}'.format(entrance_fee)} entrance fee!", delete_after=5)
                db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'AVAILABLE': True}})
                return
            else:
                if universe['GUILD'] != 'PCG':
                    crest_guild = db.queryGuildAlt({'GNAME' : universe['GUILD']})
                    if crest_guild:
                        await crown_utilities.blessguild(entrance_fee, universe['GUILD'])
                        # await ctx.send(f"{crown_utilities.crest_dict[universe['TITLE']]} | {crest_guild['GNAME']} Universe Toll Paid! 🪙{'{:,}'.format(entrance_fee)}")

        universe_selection_object = {
            "SELECTED_UNIVERSE": universe['TITLE'],
            "UNIVERSE_DATA": universe,
            "CREST_LIST": player.crestlist,
            "CREST_SEARCH": player.crestsearch,
            "COMPLETED_TALES": player.completed_tales,
            "COMPLETED_DUNGEONS": player.completed_dungeons,
            "ASSOCIATION_INFO": player.association_info,
            "CURRENTOPPONENT": currentopponent,
        }

        battle = Battle(mode, player)
        battle.set_universe_selection_config(universe_selection_object)
        await play.battle_commands(self, ctx, battle)


    async def create_scenario_battle(self, ctx, mode, player, selected_scenario):
        battle = Battle(mode, player)
        battle.selected_universe = selected_scenario["UNIVERSE"]

        selected_scenario = db.queryScenario({"TITLE": selected_scenario["TITLE"]})
        battle.set_scenario_config(selected_scenario)
        await play.battle_commands(self, ctx, battle)


    async def create_raid_battle(self, ctx, mode, player, selected_raid):
        battle = Battle(mode, player)
        battle.selected_universe = selected_raid["UNIVERSE"]
        battle.is_raid_scenario = True

        selected_raid = db.queryScenario({"TITLE": selected_raid["TITLE"]})
        battle.set_scenario_config(selected_raid)
        await play.battle_commands(self, ctx, battle)

    
    async def create_explore_battle(self, ctx, battle):
        await play.battle_commands(self, ctx, battle)

    
    async def create_pvp_battle(self, ctx, battle, p2):
        await play.battle_commands(self, ctx, battle, p2)
    
    async def create_rpg_battle(self, ctx, battle):
        await play.battle_commands(self, ctx, battle)
        
        

def setup(bot):
    BattleConfig(bot)
              