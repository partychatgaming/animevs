import db
import crown_utilities
import interactions
import datetime
import textwrap
import time
now = time.asctime()
import unique_traits as ut
from interactions import Client, ActionRow, Button, File, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension
from cogs.play import Play as play
from cogs.universe_traits.solo_leveling import set_solo_leveling_config
from cogs.quests import Quests
import asyncio

class Battle:
    def __init__(self, mode, _player):
        self.player = _player
        self.mode = mode
        self.is_tales_game_mode = False
        self.is_dungeon_game_mode = False
        self.is_explore_game_mode = False
        self.is_abyss_game_mode = False
        self.is_boss_game_mode = False
        self.is_tutorial_game_mode = False
        self.is_raid_game_mode = False
        self.is_scenario_game_mode = False
        self.is_pvp_game_mode = False
        self.is_available = True
        self.is_corrupted = False
        self.match_can_be_saved = False
        self.is_free_battle_game_mode = False
        self.is_co_op_mode = False
        self.is_duo_mode = False
        self.is_ai_opponent = False
        self.is_raid_scenario = False
        self.is_destiny = False
        self.destiny_cards = []
        self._uuid = None

        self.is_auto_battle_game_mode = False
        self.can_auto_battle = False

        self.list_of_opponents_by_name = []
        self.total_number_of_opponents = 0
        self.current_opponent_number = 0
        self.match_lineup = ""
        self.is_turn = 0
        self.turn_total = 0
        self.turn_zero_has_happened = False
        self.max_turns_allowed = 250
        self.previous_moves = ["Match has started"]
        self.previous_moves_len = 0
        self.main_battle_options = ["1", "2", "3", "4", "6"]
        self.battle_options = ["1", "2", "3", "4"]
        self.battle_buttons = []
        self.co_op_buttons = []
        self.utility_buttons = []
        self.rematch_buff = False

        self.continue_fighting = True

        self.selected_universe = ""
        self.selected_universe_full_data = ""

        self._ai_title = ""
        self._ai_arm = ""
        self._ai_summon = ""
        self._ai_opponent_card_data = ""
        self._ai_opponent_title_data = ""
        self._ai_opponent_arm_data = ""
        self._ai_opponentsummon_data = ""
        self._ai_opponentsummon_power = 0
        self._ai_opponentsummon_bond = 0
        self._ai_opponentsummon_lvl = 0
        self._ai_opponentsummon_type = ""
        self._ai_opponentsummon_name = ""
        self._ai_opponentsummon_universe = ""
        self._ai_opponentsummon_ability_name = ""
        self._ai_opponentsummon_image = ""
        self._deck_selection = 0
        self._previous_ai_move = ""
        self._tactics = []

        self.difficulty = _player.difficulty
        self.is_easy_difficulty = False
        self.is_hard_difficulty = False
        self.is_normal_difficulty = False

        self.health_buff = 0
        self.health_debuff = 0
        self.stat_buff = 0
        self.stat_debuff = 0
        self.ap_buff = 0
        self.ap_debuff = 0
        self.co_op_stat_bonus = 0
        self.co_op_health_bonus = 0
        self.are_teammates = False
        self.are_family_members = False

        # Universal Elemetal Buffs
        self._wind_buff = 0

        self._ai_opponent_card_lvl = 0
        self._ai_opponentsummon_bond = 0
        self._ai_can_usesummon = False
        self._ai_combo_counter = 0

        self._boss_fought_already = False
        self._boss_data = ""

        self.completed_tales = self.player.completed_tales
        self.completed_dungeons = self.player.completed_dungeons
        self.player_association = ""
        self.name_of_boss = ""
        self._ai_opponent_card_lvl = 0
        self.match_has_ended = False

        self.bank_amount = 0
        self.fam_reward_amount = 0

        # Messages
        self.abyss_message = ""

        # Abyss / Scenario / Explore Config
        self.abyss_floor = ""
        self.abyss_card_to_earn = ""
        self.abyss_banned_card_tiers = ""
        self.abyss_player_card_tier_is_banned = False
        self.scenario_data = ""
        self.scenario_easy_drops = []
        self.scenario_normal_drops = []
        self.scenario_hard_drops = []
        self.scenario_has_drops = False
        self.explore_type = ""
        self.bounty = ""

        # Boss Important Descriptions
        self._arena_boss_description = ""
        self._arenades_boss_description = ""
        self._entrance_boss_description = ""
        self._description_boss_description = ""
        self._welcome_boss_description = ""
        self._feeling_boss_description = ""
        self._powerup_boss_description = ""
        self._aura_boss_description = ""
        self._assault_boss_description = ""
        self._world_boss_description = ""
        self._punish_boss_description = ""
        self._rmessage_boss_description = ""
        self._rebuke_boss_description = ""
        self._concede_boss_description = ""
        self._wins_boss_description = ""
        self._boss_embed_message = ""
        self._ai_is_boss = False

        # Boss Specific Moves
        self._turns_to_skip = 0
        self._damage_check_count = 0
        self._has_resurrect = False

        # AI Tutorial Config
        self.raidActive = False
        self.tutorial_basic = False
        self.tutorial_special = False
        self.tutorial_ultimate = False
        self.tutorial_enhancer = False
        self.tutorial_block = False
        self.tutorial_resolve = False
        self.tutorial_focus = False
        self.tutorial_summon = False
        self.tutorial_opponent_focus = False
        self.all_tutorial_tasks_complete = False
        self.double_focus_check = False
        self._tutorial_message = ""
        self.tutorial_did = 0
        
        #Raid Config
        self._is_title_match = False
        self._is_training_match = False
        self._is_test_match = False
        self._is_bounty_match = False
        self._shield_name = ""
        self._hall_info = ""
        self._raid_hall = ""
        self._shield_guild = ""
        self._player_guild = ""
        self._association_info = ""
        self._association_name = ""
        self._raid_end_message = ""
        self._raid_fee = 0
        self._raid_bounty = 0
        self._raid_bonus = 0
        self._victory_streak = 0
        self._hall_defense = 0
        self._raid_bounty_plus_bonus = 0

        self.player1 = _player
        self.player1_card = None
        self.player1_title = None
        self.player1_arm = None
        self.player2 = None
        self.player2_card = None
        self.player2_title = None
        self.player2_arm = None
        self.player3 = None
        self.player3_card = None
        self.player3_title = None
        self.player3_arm = None

        
        self.blocking_traits = ['Attack On Titan',
                           'Bleach',
                           'Black Clover',
                           'Death Note'
        ]
        self.focus_traits = ['Black Clover', 
                        'Dragon Ball Z',
                        'One Punch Man',
                        'League Of Legends',
                        'Solo Leveling',
                        'One Piece',
                        'Naruto',
                        'Digimon',
                        'Crown Rift Madness'
        ]
        self.opponent_focus_traits = ['7ds',
                                 'Souls',
                                 'One Punch Man',
                                 
            
        ]
        self.resolve_traits = ['My Hero Academia',
                          'One Piece',
                          'Pokemon',
                          'Digimon',
                          'Fate',
                          'League Of Legends',
                          'Bleach',
                          'Naruto',
                          'Attack On Titan',
                          'God Of War',
                          'Souls',
                          'Crown Rift Madness'
            
        ]
        self.set_up_traits = ['Demon Slayer',
                         'Solo Leveling',
                         'Crown Rift Slayers',
                         'Soul Eater',
                         'Crown Rift Awakening',
                         'YuYu Hakusho',
                         'Death Note',
                         'Chainsawman',
                         'Dragon Ball Z'
                        
        ]
        
        self.summon_traits = ['7ds',
                         'Persona'
            
        ]
        

        self.player1_wins = False
        self.player2_wins = False
        self.battle_mode = ""


        if self.mode in crown_utilities.PVP_M:
            self.is_pvp_game_mode = True
            self.total_number_of_opponents = 1
            self.battle_mode = "PVP"   

        if self.mode in crown_utilities.AUTO_BATTLE_M:
            self.is_auto_battle_game_mode = True
            self.is_ai_opponent = True

        if self.mode in crown_utilities.DUO_M:
            self.is_duo_mode = True
            self.is_ai_opponent = True
            self.starting_match_title = f"Duo Battle! ({self.current_opponent_number + 1}/{self.total_number_of_opponents})"

        if self.mode in crown_utilities.CO_OP_M:
            self.is_co_op_mode = True
            self.is_ai_opponent = True
            self.starting_match_title = f"Co-op Battle! ({self.current_opponent_number + 1}/{self.total_number_of_opponents})"

        if self.mode in crown_utilities.RAID_M:
            self.is_raid_game_mode = True
            self.is_ai_opponent = True
            self.total_number_of_opponents = 1
            self.starting_match_title = f"Raid Battle!"
            self.can_auto_battle = True
            self.is_boss_game_mode = True
            self.is_raid_scenario = True
            self.battle_mode = "RAID"


        if self.mode in crown_utilities.TALE_M:
            self.is_tales_game_mode = True
            self.is_ai_opponent = True
            self._ai_opponentsummon_lvl = 5
            self._ai_opponentsummon_bond = 1
            self._ai_opponent_card_lvl = 10
            self.can_auto_battle = True
            self.bank_amount = 50000
            self.fam_reward_amount = 500000
            self.battle_mode = "TALES"

        
        if self.mode in crown_utilities.DUNGEON_M:
            self.is_dungeon_game_mode = True
            self.is_ai_opponent = True
            self._ai_opponentsummon_lvl = 10
            self._ai_opponentsummon_bond = 3
            self._ai_opponent_card_lvl = 450
            self.health_buff = self.health_buff + 1000
            self.stat_buff = self.stat_buff + 100
            self.ap_buff = self.ap_buff + 80
            self.bank_amount = 500000
            self.fam_reward_amount = 2000000
            self.can_auto_battle = True
            self.battle_mode = "DUNGEON"


        if self.mode in crown_utilities.BOSS_M:
            self.is_boss_game_mode = True
            self.is_ai_opponent = True
            self._ai_opponentsummon_lvl = 15
            self._ai_opponentsummon_bond = 4
            self._ai_opponent_card_lvl = 1000
            self.health_buff = self.health_buff + 3500
            self.stat_buff = self.stat_buff + 100
            self.ap_buff = self.ap_buff + 350
            self.total_number_of_opponents = 1
            self.starting_match_title = "👿 BOSS BATTLE!"
            self.bank_amount = 25000000
            self.fam_reward_amount = 50000000


        if self.mode == crown_utilities.ABYSS:
            self.is_abyss_game_mode = True
            self.is_ai_opponent = True
            self.can_auto_battle = True

        
        if self.mode == crown_utilities.SCENARIO:
            self.is_scenario_game_mode = True
            self.is_ai_opponent = True
            self.can_auto_battle = True
            self.battle_mode = "SCENARIO"

        
        if self.mode == crown_utilities.EXPLORE:
            self.is_explore_game_mode = True
            self.is_ai_opponent = True
            self.can_auto_battle = True
            self.total_number_of_opponents = 1
            self.starting_match_title = f"✅ Explore Battle is about to begin!"
            self.battle_mode = "EXPLORE"

        if self.difficulty == "EASY":
            self.is_easy_difficulty = True
            self.health_debuff = self.health_debuff + -500
            self.stat_debuff = self.stat_debuff + 100
            self.ap_debuff = self.ap_debuff + 15
            self.bank_amount = 500
            self.fam_reward_amount = 100

        
        if self.difficulty == "NORMAL":
            self.is_normal_difficulty = True
            self.bank_amount = 2500
            self.fam_reward_amount = 1500
        
        if self.difficulty == "HARD":
            self.is_hard_difficulty = True
            self.health_buff = self.health_buff + 3000
            self.stat_buff = self.stat_buff + 200
            self.ap_buff = self.ap_buff + 150
            self.bank_amount = self.bank_amount + 25000
            self.fam_reward_amount = self.fam_reward_amount + 25000

        if self.is_ai_opponent:
            self._ai_can_usesummon = True
            
        if self.is_raid_game_mode:
            self._ai_can_usesummon = False

        if self.is_tutorial_game_mode:
            self.starting_match_title = "Click Start Match to Begin the Tutorial!"
        

        
    def set_universe_selection_config(self, universe_selection_object):
        if universe_selection_object:
            self.selected_universe = universe_selection_object['SELECTED_UNIVERSE']
            self.selected_universe_full_data = universe_selection_object['UNIVERSE_DATA']
            self.crestlist = universe_selection_object['CREST_LIST']
            self.crestsearch = universe_selection_object['CREST_SEARCH']
            self.current_opponent_number =  universe_selection_object['CURRENTOPPONENT']

            if self.is_dungeon_game_mode:
                self.list_of_opponents_by_name = self.selected_universe_full_data['DUNGEONS']
                self.total_number_of_opponents = len(self.list_of_opponents_by_name)
            if self.is_tales_game_mode:
                self.list_of_opponents_by_name = self.selected_universe_full_data['CROWN_TALES']
                self.total_number_of_opponents = len(self.list_of_opponents_by_name)

            if self.is_boss_game_mode:
                self.name_of_boss = universe_selection_object['BOSS_NAME']
                self.player_association = universe_selection_object['ASSOCIATION_INFO']
                if self.player.boss_fought:
                    self._boss_fought_already = True
                    
            if self.crestsearch:
                self.player_association = universe_selection_object['ASSOCIATION_INFO']
            else:
                self.player_association = "PCG"
            self.starting_match_title = f"✅ Start Battle!  ({self.current_opponent_number + 1}/{self.total_number_of_opponents})"


    def get_starting_match_title(self):
        self.starting_match_title = f"✅ Start Battle!  ({self.current_opponent_number + 1}/{self.total_number_of_opponents})"
        if self.is_tutorial_game_mode:
            self.starting_match_title = "Click Start Match to Begin the Tutorial!"
        return  self.starting_match_title

    def set_abyss_config(self, player):
        try:
            if self.is_easy_difficulty:
                self.abyss_message = "The Abyss is unavailable on Easy self.mode! Use /difficulty to change your difficulty setting."
                return

            checks = db.queryCard({'NAME': player.equipped_card})
            abyss = db.queryAbyss({'FLOOR': player.level})

            if not abyss:
                self.abyss_message = "You have climbed out of :new_moon: **The Abyss**! Use /exchange to **Prestige**!"
                return

            self.is_ai_opponent = True
            self.is_abyss_game_mode = True
            self.list_of_opponents_by_name = abyss['ENEMIES']
            card_to_earn = self.list_of_opponents_by_name[-1] 
            self.total_number_of_opponents = len(self.list_of_opponents_by_name)
            self._ai_opponent_card_lvl = int(abyss['SPECIAL_BUFF'])
            self.abyss_floor = abyss['FLOOR']
            self.abyss_card_to_earn = self.list_of_opponents_by_name[-1] 
            self._ai_title = abyss['TITLE']
            self._ai_arm = abyss['ARM']
            self._ai_summon = abyss['PET']
            self.abyss_banned_card_tiers = abyss['BANNED_TIERS']
            self.abyss_banned_tier_conversion_to_string = [str(tier) for tier in self.abyss_banned_card_tiers]
            licon = "🔰"
            if self._ai_opponent_card_lvl>= 200:
                licon ="🔱"
            if self._ai_opponent_card_lvl>= 700:
                licon ="⚜️"
            if self._ai_opponent_card_lvl >= 999:
                licon = "🏅"
            if self.abyss_floor in crown_utilities.ABYSS_REWARD_FLOORS:
                unlockable_message = f"⭐ Drops on this Floor\nUnlockable Card: **{card_to_earn}**\nUnlockable Title: **{self._ai_title}**\nUnlockable Arm: **{self._ai_arm}**\n"
            else:
                unlockable_message = ""

            if checks['TIER'] in self.abyss_banned_card_tiers and self.abyss_floor >49:
                self.abyss_player_card_tier_is_banned = True


            embedVar = Embed(title=f":new_moon: Abyss Floor {str(self.abyss_floor)}  ⚔️{len(self.list_of_opponents_by_name)}", description=textwrap.dedent(f"""
            \n{unlockable_message}\n{licon} | **Floor Level** {self._ai_opponent_card_lvl}\n🎗️ | **Floor Title** {self._ai_title}\n🦾 | **Floor Arm** {self._ai_arm}\n🧬 | **Floor Summon** {self._ai_summon}
            """))
            if self.abyss_banned_card_tiers and self.abyss_floor > 49:
                embedVar.add_field(name="🀄 Banned Card Tiers", value="\n".join(self.abyss_banned_tier_conversion_to_string),
                                inline=True)
            embedVar.set_footer(text="Each floor must be completed all the way through to advance to the next floor.")

            return embedVar

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


    def get_unlocked_scenario_text(self):
        response = db.queryUnlockedScenarios(self.scenario_data['TITLE'])
        must_complete_list = []
        title = ""
        message = " "
        if response:
            for r in response:
                title = r['TITLE']
                message += f"\n📽️ **{r['TITLE']}** has been unlocked!\n"
        return message
    

    def set_scenario_config(self, scenario_data):
        try:
            self.battle_mode = "SCENARIO" 
            self.scenario_data = scenario_data
            self.is_scenario_game_mode = True
            self.is_ai_opponent = True
            if scenario_data['IS_RAID']:
                self.is_raid_scenario = True
            self._tactics = scenario_data['TACTICS']
            self.list_of_opponents_by_name = scenario_data['ENEMIES']
            self.total_number_of_opponents = len(self.list_of_opponents_by_name)
            self._ai_opponent_card_lvl = int(scenario_data['ENEMY_LEVEL'])
            self.selected_universe = scenario_data['UNIVERSE']
            self.is_available = scenario_data['AVAILABLE']
            self.scenario_easy_drops = scenario_data['EASY_DROPS']
            self.scenario_normal_drops = scenario_data['NORMAL_DROPS']
            self.scenario_hard_drops = scenario_data['HARD_DROPS']
            self.is_destiny = scenario_data['IS_DESTINY']
            self.destiny_cards = scenario_data['DESTINY_CARDS']

            if any((self.scenario_easy_drops, self.scenario_normal_drops, self.scenario_hard_drops)):
                self.scenario_has_drops = True

            self.starting_match_title = f"🎞️ Scenario Battle Confirm Start! ({self.current_opponent_number + 1}/{self.total_number_of_opponents})"
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


    def set_tutorial(self, opponent_did):
        bot_dids = ['837538366509154407', '845672426113466395', '263564778914578432']
        if opponent_did in bot_dids:
            self.is_tutorial_game_mode = True
            self.is_pvp_game_mode = True
            # self.is_ai_opponent = True
            self.is_turn = 0
        else:
            self.is_pvp_game_mode = True
            
    
    def create_raid(self, title_match, test_match, training_match, association, hall_info, shield_guild, player_guild): #findme
        if title_match:
            self._is_title_match = True
        if test_match:
            self._is_test_match = True
        if training_match:
            self._is_training_match = True
        if not training_match and not test_match and not title_match:
            self._is_bounty_match = True
        self._hall_info = hall_info
        self._raid_hall = hall_info['HALL']
        self._association_info = association
        self._association_name = association['GNAME']
        self._shield_name = association['SHIELD']
        self._shield_guild = shield_guild
        self._player_guild = player_guild
        self._raid_fee = int(hall_info['FEE'])
        self._raid_bounty = int(association['BOUNTY'])
        self._victory_streak = int(association['STREAK'])
        self._hall_defense = hall_info['DEFENSE']
        self._raid_bonus = int(((self._victory_streak / 100) * self._raid_bounty))
        
    
    def raid_victory(self):
        guild_query = {'GNAME': self._association_name}
        guild_info = db.queryGuildAlt(guild_query)
        bounty = guild_info['BOUNTY']
        bonus = guild_info['STREAK']
        total_bounty = int((bounty + ((bonus / 100) * bounty)))
        winbonus = int(((bonus / 100) * bounty))
        if winbonus == 0:
            winbonus = int(bounty)
        wage = int(total_bounty)
        bounty_drop = winbonus + total_bounty
        self._raid_bounty_plus_bonus = int(bounty_drop)
        self._raid_end_message = f":yen: SHIELD BOUNTY CLAIMED 🪙 {'{:,}'.format(self._raid_bounty_plus_bonus)}"
        hall_info = db.queryHall({"HALL":self._raid_hall})
        fee = hall_info['FEE']
        transaction_message = f"🛡️ {self._shield_name} loss to {self.player.disname}!"
        update_query = {'$push': {'TRANSACTIONS': transaction_message}}
        response = db.updateGuildAlt(guild_query, update_query)
        if self._is_title_match:
            if self._is_test_match:
                self._raid_end_message  = f":flags: {self._association_name} DEFENSE TEST OVER!"
            elif self._is_training_match:
                self._raid_end_message  = f":flags: {self._association_name} TRAINING COMPLETE!"
            else:
                transaction_message = f"🛡️{self.player.name} becomes the new Shield!"
                update_query = {'$push': {'TRANSACTIONS': transaction_message}}
                response = db.updateGuildAlt(guild_query, update_query)
                newshield = db.updateGuild(guild_query, {'$set': {'SHIELD': str(self._player.disname)}})
                newshieldid = db.updateGuild(guild_query, {'$set': {'SDID': str(self._player.id)}})
                guildwin = db.updateGuild(guild_query, {'$set': {'BOUNTY': winbonus, 'STREAK': 1}})
                self._raid_end_message  = f":flags: {self._association_name} SHIELD CLAIMED!"
                prev_team_update = {'$set': {'SHIELDING': False}}
                remove_shield = db.updateTeam({'TEAM_NAME': str(self._shield_guild)}, prev_team_update)
                update_shielding = {'$set': {'SHIELDING': True}}
                add_shield = db.updateTeam({'TEAM_NAME': str(self._player_guild)}, update_shielding)
        else:
            transaction_message = f"🆚 {self.player.disname} defeated {self._shield_name}! They claimed the 🪙 {'{:,}'.format(self._raid_bounty_plus_bonus)} Bounty!"
            update_query = {'$push': {'TRANSACTIONS': transaction_message}}
            response = db.updateGuildAlt(guild_query, update_query)
            guildloss = db.updateGuild(guild_query, {'$set': {'BOUNTY': fee, 'STREAK': 0}})
            
        
    def set_explore_config(self, universe_data, card_data):
        try:
            self.is_explore_game_mode = True
            self.selected_universe_full_data = universe_data
            self._ai_opponent_card_data = card_data
            self.selected_universe = universe_data['TITLE']
            if self.is_dungeon_game_mode or self._ai_opponent_card_lvl >= 350:
                summon_query = {'UNIVERSE': universe_data['TITLE'], 'DROP_STYLE': "DUNGEON"}
                arm_query = {'UNIVERSE': universe_data['TITLE'], 'DROP_STYLE': "DUNGEON", 'ELEMENT': ""}

            if self.is_tales_game_mode or self._ai_opponent_card_lvl < 350:
                summon_query = {'UNIVERSE': universe_data['TITLE'], 'DROP_STYLE': "TALES"}
                arm_query = {'UNIVERSE': universe_data['TITLE'], 'DROP_STYLE': "TALES", 'ELEMENT': ""}

            self._ai_opponent_title_data = db.get_random_title({"UNIVERSE": universe_data['TITLE']}, self.player1)
            self._ai_opponent_arm_data = db.get_random_arm(arm_query, self.player1)
            self._ai_summon = db.get_random_summon_name(summon_query)
            self._ai_opponentsummon_data = db.querySummon({'PET': self._ai_summon})
            self._ai_opponentsummon_image = self._ai_opponentsummon_data['PATH']
            self._ai_opponentsummon_name = self._ai_opponentsummon_data['PET']
            self._ai_opponentsummon_universe = self._ai_opponentsummon_data['UNIVERSE']

            summon_passive = self._ai_opponentsummon_data['ABILITIES'][0]
            self._ai_opponentsummon_power = list(summon_passive.values())[0]
            self._ai_opponentsummon_ability_name = list(summon_passive.keys())[0]
            self._ai_opponentsummon_type = summon_passive['TYPE']
            self.is_ai_opponent = True

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


    def set_corruption_config(self):
        if self.selected_universe_full_data['CORRUPTED']:
            self.is_corrupted = True
                

    def set_who_starts_match(self):
        boss_modes = ['Boss','Cboss', 'BOSS', 'CBoss', 'CBOSS']
        if self.mode in boss_modes:
            self.is_turn = 0
        elif self.player1_card.speed >= self.player2_card.speed:
            self.is_turn = 0
        elif self.player2_card.speed > self.player1_card.speed:
            self.is_turn = 1
        else:
            self.is_turn = 0


    def get_lineup(self):
        self.match_lineup = f"{str(self.current_opponent_number + 1)}/{str(self.total_number_of_opponents)}"


    def save_match_turned_on(self):
        if self.mode not in crown_utilities.NOT_SAVE_MODES and self.difficulty != "EASY":
            self.match_can_be_saved = True
        return self.match_can_be_saved


    async def get_ai_battle_ready(self, player1_card_level):
        try:
            if not self.is_boss_game_mode:
                if any([self.is_tales_game_mode, self.is_dungeon_game_mode, self.is_scenario_game_mode, self.is_abyss_game_mode]):
                    self._ai_opponent_card_data = await asyncio.to_thread(db.queryCard, {'NAME': self.list_of_opponents_by_name[self.current_opponent_number]})
                    universe_title = self._ai_opponent_card_data['UNIVERSE']
                    universe_data = await asyncio.to_thread(db.queryUniverse, {'TITLE': {"$regex": universe_title, "$options": "i"}})

                    drop_style = "DUNGEON" if self.is_dungeon_game_mode else "TALES"
                    drop_query = {'UNIVERSE': universe_title, 'DROP_STYLE': drop_style}

                    ai_title, ai_arm, ai_summon = await asyncio.gather(
                        asyncio.to_thread(db.get_random_title, {"UNIVERSE": universe_title}, self.player1),
                        asyncio.to_thread(db.get_random_arm, drop_query, self.player1),
                        asyncio.to_thread(db.get_random_summon_name, drop_query)
                    )

                    self._ai_title = ai_title
                    self._ai_arm = ai_arm
                    self._ai_summon = ai_summon

                    if self.is_dungeon_game_mode:
                        self._ai_opponent_card_lvl = 900 if player1_card_level >= 600 else 50 + min(max(350, player1_card_level), 600)
                    elif self.is_tales_game_mode:
                        self._ai_opponent_card_lvl = 10 if player1_card_level <= 60 else min(210, (player1_card_level - 50))
                    elif self.is_scenario_game_mode or self.is_explore_game_mode:
                        drop_query['DROP_STYLE'] = "DUNGEON" if self._ai_opponent_card_lvl >= 150 else "TALES"
                        ai_title, ai_arm, ai_summon = await asyncio.gather(
                            asyncio.to_thread(db.get_random_title, {"UNIVERSE": universe_title}, self.player1),
                            asyncio.to_thread(db.get_random_arm, drop_query, self.player1),
                            asyncio.to_thread(db.get_random_summon_name, drop_query)
                        )
                        self._ai_title = ai_title
                        self._ai_arm = ai_arm
                        self._ai_summon = ai_summon

                title_data, arm_data, summon_data = await asyncio.gather(
                    asyncio.to_thread(db.queryTitle, {'TITLE': self._ai_title}),
                    asyncio.to_thread(db.queryArm, {'ARM': self._ai_arm}),
                    asyncio.to_thread(db.querySummon, {'PET': self._ai_summon})
                )

                self._ai_opponent_title_data = title_data
                self._ai_opponent_arm_data = arm_data
                self._ai_opponentsummon_data = summon_data
                self._ai_opponentsummon_image = summon_data['PATH']
                self._ai_opponentsummon_name = summon_data['PET']
                self._ai_opponentsummon_universe = summon_data['UNIVERSE']

                summon_passive = summon_data['ABILITIES'][0]
                self._ai_opponentsummon_power = list(summon_passive.values())[0]
                self._ai_opponentsummon_ability_name = list(summon_passive.keys())[0]
                self._ai_opponentsummon_type = summon_passive['TYPE']

            else:
                boss_data, card_data, title_data, arm_data, summon_data = await asyncio.gather(
                    asyncio.to_thread(db.queryBoss, {"UNIVERSE": self.selected_universe, "AVAILABLE": True}),
                    asyncio.to_thread(db.queryCard, {'NAME': self._boss_data['CARD']}),
                    asyncio.to_thread(db.queryTitle, {'TITLE': self._boss_data['TITLE']}),
                    asyncio.to_thread(db.queryArm, {'ARM': self._boss_data['ARM']}),
                    asyncio.to_thread(db.querySummon, {'PET': self._boss_data['PET']})
                )

                self._boss_data = boss_data
                self._tactics = boss_data['TACTICS']
                self._ai_opponent_card_data = card_data
                self._ai_opponent_title_data = title_data
                self._ai_opponent_arm_data = arm_data
                self._ai_opponentsummon_data = summon_data
                self._ai_opponentsummon_image = summon_data['PATH']
                self._ai_opponentsummon_name = summon_data['PET']
                self._ai_opponentsummon_universe = summon_data['UNIVERSE']
                self._ai_is_boss = True

                summon_passive = summon_data['ABILITIES'][0]
                self._ai_opponentsummon_power = list(summon_passive.values())[0]
                self._ai_opponentsummon_ability_name = list(summon_passive.keys())[0]
                self._ai_opponentsummon_type = summon_passive['TYPE']

                boss_descriptions = boss_data['DESCRIPTION']
                self._arena_boss_description = boss_descriptions[0]
                self._arenades_boss_description = boss_descriptions[1]
                self._entrance_boss_description = boss_descriptions[2]
                self._description_boss_description = boss_descriptions[3]
                self._welcome_boss_description = boss_descriptions[4]
                self._feeling_boss_description = boss_descriptions[5]
                self._powerup_boss_description = boss_descriptions[6]
                self._aura_boss_description = boss_descriptions[7]
                self._assault_boss_description = boss_descriptions[8]
                self._world_boss_description = boss_descriptions[9]
                self._punish_boss_description = boss_descriptions[10]
                self._rmessage_boss_description = boss_descriptions[11]
                self._rebuke_boss_description = boss_descriptions[12]
                self._concede_boss_description = boss_descriptions[13]
                self._wins_boss_description = boss_descriptions[14]

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


    def get_aisummon_ready(self, _card):
        _card.summon_ability_name = self._ai_opponentsummon_ability_name
        _card.summon_power = self._ai_opponentsummon_power
        _card.summon_lvl = self._ai_opponentsummon_lvl
        _card.summon_type = self._ai_opponentsummon_type
        _card.summon_bond = self._ai_opponentsummon_bond
        _card.summon_name = self._ai_opponentsummon_name
        _card.summon_image = self._ai_opponentsummon_image
        _card.summon_universe = self._ai_opponentsummon_universe


    def set_game_over(self, player1_card, player2_card, player3_card=None):
        if player1_card.health <= 0:
            self.match_has_ended = True
            self.player2_wins = True
        
        if player2_card.health <= 0:
            if self.is_tutorial_game_mode and not self.all_tutorial_tasks_complete:
                self.match_has_ended = False
                player2_card.health = 100
                return self.match_has_ended
            self.match_has_ended = True
            self.player1_wins = True

        if self.is_co_op_mode or self.is_duo_mode:
            if player3_card.health <= 0:
                self.match_has_ended = True
                self.player2_wins = True
            if player2_card.health <= 0:
                self.match_has_ended = True
                self.player1_wins = True

        if self.is_auto_battle_game_mode:
            if self.turn_total >= 250:
                self.match_has_ended = True
                self.previous_moves.append(f"⚙️{player1_card.name} could not defeat {player2_card.name} before the turn Limit. The match has ended.")
                player1_card.health = 0
        return self.match_has_ended

    
    def reset_game(self):
        self.match_has_ended = False
        self.player1_wins = False
        self.player2_wins = False
        self.turn_total = 0
        self.previous_moves = []
        self.is_auto_battle_game_mode = False


    def get_previous_moves_embed(self):
        updated_list = crown_utilities.replace_matching_numbers_with_arrow(self.previous_moves)
        msg = "\n\n".join(updated_list)
        if msg:
            return msg
        else:
            return ""
    

    def get_battle_window_title_text(self, opponent_card, your_card, partner_card=None):
        o_resolve = '🌀'
        y_resolve = '🌀'
        p_resolve = '🌀'
        o_focus = '❤️'
        y_focus = '❤️'
        p_focus = '❤️'
        
        if opponent_card.used_focus:
            o_focus = '💖'
        if your_card.used_focus:
            y_focus = '💖'
        if opponent_card.used_resolve:
            o_resolve = '⚡'
        if your_card.used_resolve:
            y_resolve = '⚡'
            
        if partner_card:
            if partner_card.used_focus:
                p_focus = '💖'
            if partner_card.used_resolve:
                p_resolve = '⚡'
        #return f"{opponent_card.name}: {o_focus}{round(opponent_card.health)} {o_resolve}{round(opponent_card.stamina)} 🗡️{round(opponent_card.attack)}/🛡️{round(opponent_card.defense)} {opponent_card._arm_message}\n{your_card.name}: {y_focus}{round(your_card.health)} {y_resolve}{round(your_card.stamina)} 🗡️{round(your_card.attack)}/🛡️{round(your_card.defense)} {your_card._arm_message}"
        if self.is_turn == 1:
            if self.is_co_op_mode or self.is_duo_mode:
                return f"{opponent_card.name}: {o_focus}{round(opponent_card.health)} {o_resolve}{round(opponent_card.stamina)} 🗡️{round(opponent_card.attack)}/🛡️{round(opponent_card.defense)} {opponent_card._arm_message}\n{partner_card.name}: {p_focus}{round(partner_card.health)} {p_resolve}{round(partner_card.stamina)} 🗡️{round(partner_card.attack)}/🛡️{round(partner_card.defense)} {partner_card._arm_message}\n{your_card.name}: {y_focus}{round(your_card.health)} {y_resolve}{round(your_card.stamina)} 🗡️{round(your_card.attack)}/🛡️{round(your_card.defense)} {your_card._arm_message}"
            else:
                return f"{opponent_card.name}: {o_focus}{round(opponent_card.health)} {o_resolve}{round(opponent_card.stamina)} 🗡️{round(opponent_card.attack)}/🛡️{round(opponent_card.defense)} {opponent_card._arm_message}\n{your_card.name}: {y_focus}{round(your_card.health)} {y_resolve}{round(your_card.stamina)} 🗡️{round(your_card.attack)}/🛡️{round(your_card.defense)} {your_card._arm_message}"
        elif self.is_turn ==3:
            return f"{opponent_card.name}: {o_focus}{round(opponent_card.health)} {o_resolve}{round(opponent_card.stamina)} 🗡️{round(opponent_card.attack)}/🛡️{round(opponent_card.defense)} {opponent_card._arm_message}\n{your_card.name}: {y_focus}{round(your_card.health)} {y_resolve}{round(your_card.stamina)} 🗡️{round(your_card.attack)}/🛡️{round(your_card.defense)} {your_card._arm_message}\n{partner_card.name}: {p_focus}{round(partner_card.health)} {p_resolve}{round(partner_card.stamina)} 🗡️{round(partner_card.attack)}/🛡️{round(partner_card.defense)} {partner_card._arm_message}"
        elif self.is_turn ==0:
            if self.is_co_op_mode or self.is_duo_mode:
                return f"{your_card.name}: {y_focus}{round(your_card.health)} {y_resolve}{round(your_card.stamina)} 🗡️{round(your_card.attack)}/🛡️{round(your_card.defense)} {your_card._arm_message}\n{partner_card.name}: {p_focus}{round(partner_card.health)} {p_resolve}{round(partner_card.stamina)} 🗡️{round(partner_card.attack)}/🛡️{round(partner_card.defense)} {partner_card._arm_message}\n{opponent_card.name}: {o_focus}{round(opponent_card.health)} {o_resolve}{round(opponent_card.stamina)} 🗡️{round(opponent_card.attack)}/🛡️{round(opponent_card.defense)} {opponent_card._arm_message}"
            else:
                return f"{your_card.name}: {y_focus}{round(your_card.health)} {y_resolve}{round(your_card.stamina)} 🗡️{round(your_card.attack)}/🛡️{round(your_card.defense)} {your_card._arm_message}\n{opponent_card.name}: {o_focus}{round(opponent_card.health)} {o_resolve}{round(opponent_card.stamina)} 🗡️{round(opponent_card.attack)}/🛡️{round(opponent_card.defense)} {opponent_card._arm_message}"
        else:
            return f"{opponent_card.name}: {o_focus}{round(opponent_card.health)} {o_resolve}{round(opponent_card.stamina)} 🗡️{round(opponent_card.attack)}/🛡️{round(opponent_card.defense)} {opponent_card._arm_message}\n{your_card.name}: {y_focus}{round(your_card.health)} {y_resolve}{round(your_card.stamina)} 🗡️{round(your_card.attack)}/🛡️{round(your_card.defense)} {your_card._arm_message}\n{partner_card.name}: {y_focus}{round(partner_card.health)} {p_resolve}{round(partner_card.stamina)} 🗡️{round(partner_card.attack)}/🛡️{round(partner_card.defense)} {partner_card._arm_message}"


    def get_battle_author_text(self, opponent_card, opponent_title, your_card, your_title, partner_card=None, partner_title=None):
        emojis = {
            'resolve': '🌀',
            'focus': '❤️',
            'used_resolve': '⚡',
            'used_focus': '💖'
        }

        card_statuses = {
            'opponent': [opponent_card, opponent_title, emojis['resolve'], emojis['focus']],
            'your': [your_card, your_title, emojis['resolve'], emojis['focus']],
            'partner': [partner_card, partner_title, emojis['resolve'], emojis['focus'] if partner_card else None]
        }

        for player, stats in card_statuses.items():
            card, title, resolve, focus = stats
            if card:
                if card.used_focus:
                    focus = emojis['used_focus']
                if card.used_resolve:
                    resolve = emojis['used_resolve']
                card_statuses[player] = [card, title, resolve, focus]


        def format_card(player):
            card, title, resolve, focus = card_statuses[player]
            if card._tactician_stack_3:
                talisman_message = f"🆚 Tactician's Talisman"
            else:
                talisman_message = f"{crown_utilities.set_emoji(card._talisman)} {card._talisman.title()} Talisman"
            return f"🎴 {card.name}\n{talisman_message}\n{focus}{round(card.health):,} {resolve}{round(card.stamina)} 🗡️{round(card.attack):,}/🛡️{round(card.defense):,}\n{title.title_battle_message_handler()} {card._arm_message}"

        if self.is_co_op_mode or self.is_duo_mode:
            if self.is_turn in [1, 0]:
                return '\n'.join(map(format_card, ['opponent']))
            elif self.is_turn == 3:
                return '\n'.join(map(format_card, ['opponent']))
            else:
                return '\n'.join(map(format_card, ['opponent']))
        else:
            return '\n'.join(map(format_card, ['opponent']))    
        
        
        # The original
        # if self.is_co_op_mode or self.is_duo_mode:
        #     if self.is_turn in [1, 0]:
        #         return '\n'.join(map(format_card, ['opponent', 'partner', 'your']))
        #     elif self.is_turn == 3:
        #         return '\n'.join(map(format_card, ['opponent', 'your', 'partner']))
        #     else:
        #         return '\n'.join(map(format_card, ['opponent', 'partner', 'your']))
        # else:
        #     return '\n'.join(map(format_card, ['opponent', 'your']))  

    def ai_battle_command(self, your_card, opponent_card):
        aiMove = 0
        stamina = your_card.stamina
        health_ratio = your_card.health / your_card.max_health
        opponent_health_low = opponent_card.health <= 500
        self_turn_mod = self.turn_total % 10

        def get_ai_enhancer_move():
            return ai_enhancer_moves(your_card, opponent_card)

        if (your_card.used_resolve and not your_card.usedsummon) or (your_card._summoner_active and not your_card.usedsummon):
            aiMove = 6
        elif your_card.is_tactician and your_card.stamina >= 20 and your_card.stamina <30:
            aiMove = 0
        elif your_card.move4enh == "WAVE" and (self_turn_mod in [0, 1]):
            aiMove = 4 if stamina >= 20 else 1
        elif your_card.barrier_active and not your_card.is_ranger:
            if stamina >= 80 and your_card.move3_element == "PSYCHIC":
                aiMove = 3
            elif stamina >= 30 and your_card.move2_element == "PSYCHIC":
                aiMove = 2
            elif stamina >= 10 and your_card.move1_element == "PSYCHIC":
                aiMove = 1
            else:
                aiMove = get_ai_enhancer_move() if stamina >= 20 else 1
        elif opponent_health_low:
            if your_card.move4enh in ["BLAST", "WAVE"] and (self_turn_mod in [0, 1] or your_card.move4enh == "BLAST"):
                aiMove = 4 if stamina >= 20 else 1
            else:
                aiMove = 1 if stamina >= 90 else (3 if stamina >= 80 else (2 if stamina >= 30 else 1))
        elif opponent_card.stamina < 10:
            aiMove = 4 if your_card.move4enh in crown_utilities.Gamble_Enhancer_Check and stamina >= 20 else 1
        elif health_ratio <= 0.5 and not your_card.used_resolve and your_card.used_focus:
            aiMove = 5
        elif your_card.universe in self.blocking_traits and stamina == 20:
            if opponent_card.attack >= your_card.defense and opponent_card.attack <= (your_card.defense * 2):
                aiMove = 0 if your_card.used_focus else 4
            elif your_card.universe == "Attack On Titan" and health_ratio <= 0.70:
                aiMove = 0
            elif opponent_card.barrier_active and opponent_card.stamina <= 20 and your_card.universe == "Bleach":
                aiMove = 0
            elif self_turn_mod == 0 and your_card.universe == "Bleach":
                aiMove = 0
            elif your_card.universe == "Death Note" and your_card.max_health >= 1500:
                aiMove = 0
            elif your_card.barrier_active:
                aiMove = 4
            else:
                aiMove = 1
        elif stamina >= 160:
            aiMove = 3
        elif stamina >= 150:
            aiMove = 1
        elif stamina >= 140:
            aiMove = 3
        elif stamina >= 130:
            aiMove = 1
        elif stamina >= 120:
            aiMove = 3
        elif stamina >= 110:
            aiMove = 2
        elif stamina >= 100:
            if your_card.move4enh in crown_utilities.Gamble_Enhancer_Check or your_card.move4enh in crown_utilities.Healer_Enhancer_Check:
                aiMove = 3
            elif your_card.move4enh in crown_utilities.Support_Enhancer_Check or your_card.move4enh in crown_utilities.Stamina_Enhancer_Check or your_card.move4enh in crown_utilities.Turn_Enhancer_Check:
                aiMove = 4
            else:
                aiMove = 1
        elif stamina >= 90:
            aiMove = 3 if your_card.universe not in self.blocking_traits else 0
        elif stamina >= 80:
            aiMove = 3
        elif stamina >= 70:
            aiMove = 1 if your_card.move4enh in crown_utilities.Gamble_Enhancer_Check else get_ai_enhancer_move()
        elif stamina >= 60:
            if not your_card.used_resolve and your_card.used_focus:
                aiMove = 5
            elif not your_card.used_focus:
                aiMove = 2
            else:
                aiMove = 1
        elif stamina >= 50:
            if not your_card.used_resolve and your_card.used_focus:
                aiMove = 5
            elif not your_card.used_focus:
                aiMove = 2
            elif your_card.move4enh in crown_utilities.Support_Enhancer_Check or your_card.move4enh in crown_utilities.Stamina_Enhancer_Check:
                aiMove = 4
            else:
                aiMove = 1
        elif stamina >= 40:
            aiMove = 2
        elif stamina >= 30:
            aiMove = get_ai_enhancer_move()
        elif stamina >= 20:
            if your_card.move4enh in crown_utilities.Gamble_Enhancer_Check:
                aiMove = 1
            elif your_card.move4enh in crown_utilities.Support_Enhancer_Check or your_card.move4enh in crown_utilities.Stamina_Enhancer_Check:
                aiMove = 1
            else:
                aiMove = 4
        elif stamina >= 10:
            aiMove = 1
        else:
            aiMove = 0

        self._previous_ai_move = aiMove

        # Hard Mode AI
        if self.is_hard_difficulty:
            self._combo_counter = 0
            if aiMove == self._previous_ai_move:
                self._combo_counter += 1
                if self._combo_counter == 2:
                    self._combo_counter = 0
                    if self._previous_ai_move == 0:
                        if stamina >= 80:
                            aiMove = 3
                        elif stamina >= 30:
                            aiMove = 2
                        elif stamina >= 20 and (your_card.move4enh == "LIFE" or your_card.move4enh in crown_utilities.Damage_Enhancer_Check):
                            aiMove = 4
                        else:
                            aiMove = 1
                    elif self._previous_ai_move == 1:
                        aiMove = 4 if your_card.barrier_active else (3 if stamina >= 80 else (2 if stamina >= 30 else 1))
                    elif self._previous_ai_move == 2:
                        aiMove = 4 if stamina >= 120 else (0 if stamina >= 100 else (3 if stamina >= 80 else 1))
                    elif self._previous_ai_move == 3:
                        aiMove = 1 if stamina >= 120 else (2 if stamina >= 100 else (4 if stamina >= 80 else 1))
                    elif self._previous_ai_move == 4:
                        aiMove = 2 if stamina >= 120 else (1 if stamina >= 100 else (3 if stamina >= 80 else 1))
                    else:
                        aiMove = 4 if stamina >= 120 else (3 if stamina >= 100 else (1 if stamina >= 80 else 1))
                self._previous_ai_move = aiMove

        return aiMove


    def add_to_battle_log(self, msg):
        if msg:
            self.previous_moves.append(msg)


    def set_battle_options(self, your_card, opponent_card, companion_card=None):
        b_butts = []
        u_butts = []
        c_butts = []
        if self.is_turn == 3:
            options = ["q", "Q", "0", "1", "2", "3", "4", "7"]
            if your_card.used_focus:
                if your_card.used_resolve:
                    options += [6]
                else:
                    options += [5]
            if your_card._summoner_active:
                options += ['6']
            self.battle_options = options
        else:
            options = ["q", "Q", "0", "1", "2", "3", "4"]
            if self.is_co_op_mode:
                options += ["7", "8", "9", "s", "b"]
            else:
                options += ["s"]
            if your_card.used_focus:
                if your_card.used_resolve:
                    options += ['6']
                else:
                    options += ['5']
            if your_card._summoner_active:
                options += ['6']
            self.battle_options = options

        if your_card.stamina >= 10:
            # if your_card.universe == "Souls" and your_card.used_resolve:
            #     b_butts.append(
            #         Button(
            #             style=ButtonStyle.GREEN,
            #             label=f"{your_card.move2_emoji} 10",
            #             custom_id=f"{self._uuid}|1"
            #         )
            #     )
            # else:
            b_butts.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label=f"{your_card.move1_emoji}10",
                    custom_id=f"{self._uuid}|1"
                )
            )

        if your_card.stamina >= 30:
            # if your_card.universe == "Souls" and your_card.used_resolve:
            #     b_butts.append(
            #         Button(
            #             style=ButtonStyle.GREEN,
            #             label=f"{your_card.move3_emoji} 30",
            #             custom_id=f"{self._uuid}|2"
            #         )
            #     )
            # else:
            b_butts.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label=f"{your_card.move2_emoji}30",
                    custom_id=f"{self._uuid}|2"
                )
            )

        if your_card.stamina >= 80:
            b_butts.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label=f"{your_card.move3_emoji}80",
                    custom_id=f"{self._uuid}|3"
                )
            )
        
        if your_card.stamina >= 20:
            b_butts.append(
                Button(
                    style=ButtonStyle.BLUE,
                    label=f"🦠20",
                    custom_id=f"{self._uuid}|4"
                )
            )

            if opponent_card.gravity_hit == False:
                u_butts.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label="🛡️Block 20",
                        custom_id=f"{self._uuid}|0"
                    )
                )
                
        if your_card.stamina >= 20 and self.is_co_op_mode and self.mode in crown_utilities.DUO_M:
            if your_card.stamina >= 20:
                c_butts = [
                    Button(
                        style=ButtonStyle.BLUE,
                        label="🦠Enhance Ally 20",
                        custom_id=f"{self._uuid}|7"
                    ),
                    Button(
                        style=ButtonStyle.BLUE,
                        label="👥Ally Assist 20",
                        custom_id=f"{self._uuid}|8"
                    ),
                    Button(
                        style=ButtonStyle.BLUE,
                        label="🛡️Ally Block 20",
                        custom_id=f"{self._uuid}|9"
                    ),
                ]
            else:
                c_butts = [           
                        Button(
                        style=ButtonStyle.RED,
                        label=f"Boost Companion",
                        custom_id=f"{self._uuid}|b"
                    )]
        
        elif (self.is_co_op_mode and self.mode not in crown_utilities.DUO_M) and your_card.stamina >= 20:
            c_butts = [
                Button(
                    style=ButtonStyle.BLUE,
                    label="Assist Companion 20",
                    custom_id=f"{self._uuid}|7"
                )
            ]
        if not self.is_raid_game_mode:
            if your_card.used_focus and your_card.used_resolve and not your_card.usedsummon or (your_card._summoner_active and not your_card.usedsummon):
                u_butts.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label="🧬Summon!",
                        custom_id=f"{self._uuid}|6"
                    )
                )

        if your_card.used_focus and not your_card.used_resolve:
            u_butts.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label="⚡Resolve!",
                    custom_id=f"{self._uuid}|5"
                )
            )
                
        u_butts.append(
            Button(
                style=ButtonStyle.GREY,
                label="Quit",
                custom_id=f"{self._uuid}|q"
            ),
        )

        if not self.is_explore_game_mode and not self.is_easy_difficulty and not self.is_abyss_game_mode and not self.is_tutorial_game_mode and not self.is_scenario_game_mode and not self.is_raid_game_mode and not self.is_pvp_game_mode and not self.is_boss_game_mode:
            u_butts.append(
                Button(
                style=ButtonStyle.RED,
                label=f"Save",
                custom_id=f"{self._uuid}|s"
            )
            )

        self.battle_buttons = b_butts
        self.utility_buttons = u_butts
        self.co_op_buttons = c_butts


    def set_levels_message(self):
        level_to_emoji = {
            0: "🔰",
            200: "🔱",
            700: "⚜️",
            999: "🏅"
        }
        def get_player_message(card):
            lvl = int(card.card_lvl)
            emoji = "🔰"
            
            if lvl >= 1000:
                emoji = "🏅"
            elif lvl >= 700:
                emoji = "⚜️"
            elif lvl >=200:
                emoji = "🔱"
            return f"[{crown_utilities.class_emojis[card.card_class]}] {emoji} {lvl} {card.name}"

        p1_msg = get_player_message(self.player1_card)
        p2_msg = get_player_message(self.player2_card)
        message = f"{crown_utilities.set_emoji(self.player1_card._talisman)} | {p1_msg}\n{self.player1_card.universe_crest} 🆚 {self.player2_card.universe_crest}\n{crown_utilities.set_emoji(self.player2_card._talisman)} | {p2_msg}"

        if self.is_co_op_mode:
            p3_msg = get_player_message(self.player3_card)
            message = f"{crown_utilities.set_emoji(self.player1_card._talisman)} | {p1_msg}\n{crown_utilities.set_emoji(self.player3_card._talisman)} | {p3_msg}\n🆚\n{crown_utilities.set_emoji(self.player2_card._talisman)} | {p2_msg}"

        return message


    def error_end_match_message(self):
        response = ""
        if not self.is_abyss_game_mode and not self.is_scenario_game_mode:
            if not self.is_tutorial_game_mode:
                if self.is_pvp_game_mode:
                    response = f"Your 🆚 timed out. Your channel has been closed"
                elif self.is_boss_game_mode:
                    response = f"Your Boss Fight timed out. Your channel has been closed."
                else:
                    response = f"Your Game timed out. Your channel has been closed but your spot in the tales has been saved where you last left off."
            else:
                response = f"Your Game timed out. Your channel has been closed, restart the tutorial with **/play**."
        else:
            response = f"Your game timed out. Your channel has been closed and your Abyss Floor was Reset."
        self.match_has_ended = True
        return response


    def get_battle_time(self):
        wintime = time.asctime()
        starttime = time.asctime()
        h_gametime = starttime[11:13]
        m_gametime = starttime[14:16]
        s_gametime = starttime[17:19]
        h_playtime = int(wintime[11:13])
        m_playtime = int(wintime[14:16])
        s_playtime = int(wintime[17:19])
        gameClock = crown_utilities.getTime(int(h_gametime), int(m_gametime), int(s_gametime), h_playtime, m_playtime,
                            s_playtime)
        
        if int(gameClock[0]) == 0 and int(gameClock[1]) == 0:
            return f"Battle Time: {gameClock[2]} Seconds."
        elif int(gameClock[0]) == 0:
            return f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds."
        else:
            return f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds."
        
        
    def saved_game_embed(self, player_card, opponent_card, companion_card = None):
        picon = "⚔️"
        save_message = "Tale"
        if self.is_dungeon_game_mode:
            save_message = "Dungeon"
            picon = "🔥"

                
        embedVar = Embed(title=f"💾 {opponent_card.universe} {save_message} Saved!")
        embedVar.add_field(name="💽 | Saved Data",
                                value=f"🌍 | **Universe**: {opponent_card.universe}\n{picon} | **Progress**: {self.current_opponent_number + 1}\n🎴 | **Opponent**: {opponent_card.name}")
        embedVar.set_footer(text=f"{self.get_previous_moves_embed()}"f"\n{self.get_battle_time()}")
        return embedVar

    def get_tutorial_message(self, player_card):
        incomplete_task = '❌'
        complete_task = '✅'

        basic_task = incomplete_task
        special_task = incomplete_task
        ultimate_task = incomplete_task
        enhancer_task = incomplete_task
        block_task = incomplete_task
        resolve_task = incomplete_task
        focus_task = incomplete_task
        summon_task = incomplete_task
        opponent_focus_task = incomplete_task

        if self.tutorial_basic == True:
            basic_task = complete_task
        if self.tutorial_special == True:
            special_task = complete_task
        if self.tutorial_ultimate == True:
            ultimate_task = complete_task
        if self.tutorial_enhancer == True:
            enhancer_task = complete_task
        if self.tutorial_block == True:
            block_task = complete_task
        if self.tutorial_focus == True:
            focus_task = complete_task
        if self.tutorial_resolve == True:
            resolve_task = complete_task
        if self.tutorial_summon == True:
            summon_task = complete_task
        #If all of the above are true, create a variable that will be used to end the tutorial match
        self.all_tutorial_tasks_complete = (basic_task == complete_task and special_task == complete_task and ultimate_task == complete_task and enhancer_task == complete_task and block_task == complete_task and resolve_task == complete_task and focus_task == complete_task and summon_task == complete_task)
        if self.all_tutorial_tasks_complete:
            return f"✅| All Tutorial Tasks Complete!\n🌟| Defeat the Training Dummy!"
        if player_card.is_summoner and not self.tutorial_focus:
            return f"*{basic_task}{player_card.move1_emoji}10|{special_task}{player_card.move2_emoji}30|{ultimate_task}{player_card.move3_emoji}80|{enhancer_task}🦠20\n{block_task}🛡️Block 20\n{focus_task}🌀Focus\n{summon_task}🧬Summon!*"
        if self.tutorial_focus == True and self.tutorial_resolve == True:
            return f"*{basic_task}{player_card.move1_emoji}10|{special_task}{player_card.move2_emoji}30|{ultimate_task}{player_card.move3_emoji}80|{enhancer_task}🦠20\n{block_task}🛡️Block 20\n{focus_task}🌀Focus\n{resolve_task}⚡Resolve!\n{summon_task}🧬Summon!*"
        elif self.tutorial_focus == True:
            if player_card.is_summoner:
                return f"*{basic_task}{player_card.move1_emoji}10|{special_task}{player_card.move2_emoji}30|{ultimate_task}{player_card.move3_emoji}80|{enhancer_task}🦠20\n{block_task}🛡️Block 20\n{focus_task}🌀Focus\n{resolve_task}⚡Resolve!\n{summon_task}🧬Summon!*"
            else:
                return f"*{basic_task}{player_card.move1_emoji}10|{special_task}{player_card.move2_emoji}30|{ultimate_task}{player_card.move3_emoji}80|{enhancer_task}🦠20\n{block_task}🛡️Block 20\n{focus_task}🌀Focus\n{resolve_task}⚡Resolve!*"
        else:
            return f"*{basic_task}{player_card.move1_emoji}10|{special_task}{player_card.move2_emoji}30|{ultimate_task}{player_card.move3_emoji}80|{enhancer_task}🦠20\n{block_task}🛡️Block 20\n{focus_task}🌀Focus*"

    
    def close_pve_embed(self, player_card, opponent_card, companion_card = None):
        picon = "⚔️"
        close_message = "Tale"
        f_message = f"💾 | Enable /autosave or use the Save button to maintain progress!"
        db_adjustment = 1
        if self.is_dungeon_game_mode:
            close_message = "Dungeon"
            picon = "🔥"
        if self.is_boss_game_mode:
            close_message = "Boss"
            picon = "👹"
            f_message = f"🪦 | You fail to claim {opponent_card.name}'s Soul"
        if self.is_abyss_game_mode:
            close_message = "Abyss"
            picon = ":new_moon:"
            f_message = f"🪦 | The Abyss Claims Another..."
        if self.is_explore_game_mode:
            close_message = "Explore Battle"
            picon = "🌌"
            f_message = f"🪦 | Explore Battle Failed!"
        if self.is_scenario_game_mode:
            close_message = "Scenario Battle"
            picon = "📹"
            f_message = f"🪦 | Scenario Ended."
        if self.is_raid_scenario:
            close_message = "Raid Battle"
            picon = "💀"
            f_message = f"🪦 | Scenario Raid Ended."
        if self.is_raid_game_mode:
            close_message = "Arena Battle"
            picon = "⛩️"
            f_message = f"🪦 | Unsuccessful Arena."
        if self.is_tutorial_game_mode:
            close_message = "Tutorial Battle"
            picon = "🧠"
            f_message = f"🧠 | Tutorial will teach you about Game Mechanics and Card Abiltiies!"
            
            
        embedVar = Embed(title=f"{picon} {opponent_card.universe} {close_message} Ended!", description=textwrap.dedent(f"""
            """))
        embedVar.add_field(name=f"{picon} | Last Battle : {self.current_opponent_number + db_adjustment}",
                                value=f"🎴 | **Opponent**: {opponent_card.name}")
        
        embedVar.set_footer(text=f_message)
        return embedVar
    

    def close_pvp_embed(self, player, opponent):
        picon = "🆚"
        icon1 = "1️⃣"
        icon2 = "2️⃣"
        close_message = "PVP"
        f_message = f"🫂 | Try Co-Op Battle and Conquer The Multiverse Together!"
        if self.is_tutorial_game_mode:
            close_message = "Tutorial"
            icon2 = "🧑‍🏫"
            f_message = f"🧠 | Tutorial will teach you about Game Mechanics and Card Abiltiies!"
        if self.is_raid_game_mode:
            close_message = "Raid"
            icon2 = "🛡️"
            f_message = f"⛩️ | Raid Associations to Claim the Bounty or Claim The Shield Title"
            

                
        embedVar = Embed(title=f"{picon} {close_message} Ended!", description=textwrap.dedent(f"""
            {player.disname} 🆚 {opponent.disname}
            """))
        embedVar.add_field(name=f"{icon1} | {player.disname}",
                                value=f"🎴 | {player.equipped_card}\n🎗️ | {player.equipped_title}\n🦾 | {player.equipped_arm}\n🧬 | {player._equipped_summon_name}")
        embedVar.add_field(name=f"{icon2} | {opponent.disname}",
                                value=f"🎴 | {opponent.equipped_card}\n🎗️ | {opponent.equipped_title}\n🦾 | {opponent.equipped_arm}\n🧬 | {opponent._equipped_summon_name}")
        embedVar.set_footer(text=f_message)
        return embedVar
    
    def tutorial_messages(self, player_card, opponent_card, message_type):
        embedVar = False
        if message_type == 'BASIC':
            embedVar = Embed(title=f":boom:Basic Attack!",
                                    description=f"**Basic Attacks** cost **10 ST(Stamina)**\n")
            embedVar.add_field(
                name=f"{player_card.move1_emoji} {player_card.move1} inflicts {player_card.move1_element.title()}",
                value=f"**{player_card.move1_element}** : *{crown_utilities.get_element_mapping(player_card.move1_element)}*\n")
            # embedVar.set_footer(
            #     text=f"Basic Attacks are great when you are low on stamina. Enter Focus State to Replenish!")
            return embedVar
        elif message_type == 'SPECIAL':
            embedVar = Embed(title=f":comet:Special Attack!",
                                    description=f"**Special Attacks** cost **30 ST(Stamina)**\n")
            embedVar.add_field(
                name=f"{player_card.move2_emoji} {player_card.move2} inflicts {player_card.move2_element.title()}",
                value=f"**{player_card.move2_element}** : *{crown_utilities.get_element_mapping(player_card.move2_element)}*\n")
            # embedVar.set_footer(
            #     text=f"Special Attacks are used to control the Focus Count! Use Them to Maximize your Focus and build stronger Combos!")
            return embedVar
        elif message_type == "ULTIMATE":
            embedVar =  Embed(title=f":rosette:Ultimate Move!",
                                    description=f"**Ultimate Move** cost **80 ST(Stamina)**\n")
            embedVar.add_field(
                name=f"{player_card.move3_emoji} {player_card.move3} inflicts {player_card.move3_element.title()}",
                value=f"**{player_card.move3_element}** : *{crown_utilities.get_element_mapping(player_card.move3_element)}*\n")
            # embedVar.add_field(name=f"Ultimate GIF",
            #                 value="Using your ultimate move also comes with a bonus GIF to deliver that final blow!\n*Enter performance mode to disable GIFs\n/performace*")
            # embedVar.set_footer(
            #     text=f"Ultimate moves will consume most of your ST(Stamina) for Incredible Damage! Use Them Wisely!")
            return embedVar
        elif message_type == "ENHANCER":
            self.tutorial_enhancer = True
            embedVar = Embed(title=f"🦠Enhancers!",
                                    description=f"**Enhancers** cost **20 ST(Stamina)** to Boost your Card or Debuff Your Opponent!\n")
            embedVar.add_field(
                name=f"🦠 {player_card.move4} is a {player_card.move4enh.title()}",
                value=f"\n**{player_card.move4enh}** : *{crown_utilities.get_enhancer_mapping(player_card.move4enh)}*\n")
            # embedVar.set_footer(
            #     text=f"Use /help to view a full list of Enhancers! Look for the {player_card.move4enh} Enhancer")
            return embedVar
        elif message_type == "SUMMON":
            self.tutorial_summon = True
            embedVar = Embed(title=f"{player_card.name} Summoned 🧬 {player_card.summon_name}",
                             description=f"**{player_card.summon_name}** used their {player_card.summon_emoji} {player_card.summon_type} ability\n")
            embedVar.add_field(name=f"Summon Rest",
                            value="*You can use _🧬Summons_ once per Focus without losing a turn*\n")
            if player_card.is_summoner:
                protections = ['BARRIER', 'PARRY']
                if player_card.summon_type in protections:
                    summoner_buff = f"grants {player_card.card_tier} more protections!"
                else:
                    summoner_buff = f"is {player_card.card_tier}x more Effective!"
                embedVar.add_field(name=f"{crown_utilities.class_emojis['SUMMONER']}**Summoner Class**!",
                            value=f"*The Summoner class can call forth their ally from the start of battle! Your summon {summoner_buff}*\n")
            if player_card.universe in crown_utilities.summon_traits:
                title, text = self.summon_trait_handler(player_card)
                embedVar.add_field(name=f"\n{player_card.universe_crest} {player_card.universe} Trait: {title}",
                                value=f"{text}")
            # embedVar.set_footer(
            #     text=f"🧬Summons will Level Up and build Bond as you win battles! Train up your summons to perform better in the field!")
            return embedVar
        elif message_type == "BLOCK":
            self.tutorial_block = True
            embedVar = Embed(title=f"🛡️Blocking!",
                                    description=f"**Blocking** cost **20 ST(Stamina)** to Double your **DEF** until your next turn!\n")
            embedVar.add_field(name=f"**Damage Mitigation**",
                            value="You will take less DMG when your **DEF** is greater than your opponents **ATK**\n")
            if (player_card.is_tactician or player_card.is_tank):
                if player_card.is_tactician:
                    embedVar.add_field(name=f"{crown_utilities.class_emojis['TACTICIAN']}** Tactician Class**!",
                            value="*Enter Focus by Blocking to Strategize, Buffing yourself while debuffing your opponent*\n")
                    if player_card.stamina < 10:
                        embedVar.add_field(name=f"Stategy Point Created!**!",
                        value="*Great Job! Focusing into Block grants increasingly strong buffs or debuffs for each point gained*\n")
                if player_card.is_tank:
                    embedVar.add_field(name=f"{crown_utilities.class_emojis['TANK']}** Tank Class**!",
                            value="*On Block gain 3x Defense, instead of 2x*\n")
            if player_card.universe in crown_utilities.blocking_traits:
                title, text = self.blocking_trait_handler(player_card)
                embedVar.add_field(name=f"\n{player_card.universe_crest} {player_card.universe} Trait: {title}",
                            value=f"{text}")
            # embedVar.set_footer(
            #     text=f"Use 🛡️Block strategically to defend against your opponents strongest abilities!")
            return embedVar
        elif message_type == "FOCUS":
            embedVar = Embed(title=f"🌀{player_card.name} is **Focusing**!",
                                    description=f"Entering **Focus State** sacrifices a turn to **Heal** and Regain **90 ST(Stamina)**\n")
            embedVar.add_field(name=f"Focusing",
                            value=f"*Increase your ATK and DEF stacking bonuses with each 🌀Focus*\n")
            if player_card.universe in crown_utilities.focus_traits:
                title, text = self.focus_trait_handler(player_card, opponent_card)
                embedVar.add_field(name=f"\n{player_card.universe_crest} {player_card.universe} Trait: {title}",
                            value=f"{text}")
            # embedVar.set_footer(
            #     text=f"Pay attention to your opponents ST(Stamina). If they are entering Focus State, you may have an opportunity to attack twice!")
            return embedVar
        elif message_type == "RESOLVE":
            embedVar = Embed(title=f"⚡**Resolve Transformation**!",
                                    description=f"Sacrifice DEF to **Heal**, Boost **ATK**, and gain 🧬**Summon**!\n*Focusing will no longer increase ATK or DEF*")
            if (player_card.is_swordsman or player_card.is_tank or player_card.is_monstrosity):
                if player_card.is_swordsman:
                    embedVar.add_field(name=f"{crown_utilities.class_emojis['SWORDSMAN']}** Swordsman Class**!",
                            value=f"On Resolve gain Critical Strikes **[{player_card.class_value}]**\n")
                if player_card.is_monstrosity:
                    embedVar.add_field(name=f"{crown_utilities.class_emojis['MONSTROSITY']}** Monstrosity Class**!",
                            value=f"On Resolve gain Double Strikes **[{player_card.class_value}]**\n")
                if player_card.is_tank:
                    embedVar.add_field(name=f"{crown_utilities.class_emojis['TANK']}** Tank Class**!",
                            value=f"On Resolve gain increase your shield by 500 * Card Tier **[{500 * player_card.card_tier}]**\n")
            if player_card.universe in crown_utilities.resolve_traits:
                title, text = self.resolve_trait_handler(player_card)
                embedVar.add_field(name=f"\n{player_card.universe_crest} {player_card.universe} Trait: {title}",
                            value=f"{text}")
            # embedVar.set_footer(
            #     text=f"You can only enter ⚡Resolve once per match! Use this ability Wisely!!!")
            return embedVar
        elif message_type == "OPPONENT":
            embedVar = Embed(title=f"🌀 Your Opponent **{player_card.name}** is **Focusing**!",
                                    description=f"Your opponent will now sacrifice a turn to **Heal** and Regain **90 ST(Stamina)**\n")
            if opponent_card.universe in crown_utilities.opponent_focus_trait:
                title, text = self.opponent_focus_trait_handler(player_card, opponent_card)
                embedVar.add_field(name=f"\n{opponent_card.universe_crest} {opponent_card.universe} Trait: {title}",
                            value=f"{text}")
            return embedVar
        elif message_type == "HEALTH":
            embedVar = Embed(title=f"❤️ **{player_card.name}'s** Health Trait Activated",
                                    description=f"Some universe Traits trigger when your health reaches a certain point!")
            if player_card.universe in crown_utilities.death_traits:
                title, text = self.death_trait_handler(player_card)
                embedVar.add_field(name=f"\n{player_card.universe_crest} {player_card.universe} Trait: {title}",
                            value=f"{text}")
            return embedVar
    
    def blocking_trait_handler(self, player_card):
        name = False
        value = False
        if player_card.universe == "Attack On Titan":
            name = "Rally"
            value =f"On Block\nGain 50 * Card Tier Health and Max Health **[{50 * player_card.card_tier}]**"
            return name, value
        if player_card.universe == "Black Clover":
            name = "Grimoire"
            value =f"On Block\nIncrease ST(Stamina) by 50\nGain 25 * card tier AP **[{25 * player_card.card_tier}]**"
        if player_card.universe == "Bleach":
            name = "Spiritual Pressure"
            value =f"On Block\nStrike with your `BASIC` Attack.\nYour `BASIC` Attack: {player_card.move1_emoji} {player_card.move1} inflicts {player_card.move1_element}\n**{player_card.move1_element}** : *{crown_utilities.get_element_mapping(player_card.move1_element)}*"
        if player_card.universe == "Death Note":
            name = "Shinigami Eyes"
            value =f"On Block\nspend 50% Max Health [{.50 * player_card.max_health}] to increase turn count by 10 + Card Tier **[{10 + player_card.card_tier}]**."
        if player_card.universe == "My Hero Academia":
            name = "Plus Ultra"
            value =f"On Block\nIncrease All AP values by 20 [{player_card.my_hero_ap_buff}]"
        if player_card.universe == "YuYu Hakusho":
            name = "Meditation"
            value = f"On Block\nGain 100 * Card Tier Defense **[{100 * player_card.card_tier}]** and 10 * Card Tier AP **[{10 * player_card.card_tier}]**." 
        return name, value
    
    def summon_trait_handler(self, player_card):
        name = False
        value = False
        if player_card.universe == "Persona":
            name = "Summon Persona"
            value =f"On Summon\nstrike with your `BASIC` attack\nYour `BASIC` Attack: {player_card.move1_emoji} {player_card.move1} inflicts {player_card.move1_element}\n**{player_card.move1_element}** : *{crown_utilities.get_element_mapping(player_card.move1_element)}*"
        if player_card.universe == "Soul Eater":
            name = "Meister"
            value =f"On Summon\nSoul Eater Summons double their Protection Value and Triple their Attack damage\nSummons Always trigger Feint Attack"
        if player_card.universe == "That Time I Got Reincarnated as a Slime":
            name = "Summon Slime"
            value =f"On Summon\nGain (5 * Card Tier) Stamina**[{5 * player_card.card_tier}]**."
        return name, value
       
    def resolve_trait_handler(self, player_card):
        if player_card.universe == "Attack On Titan":
            name = "Titan Mode"
            value =f"On Resolve\nGain 100 * (Focus Count * Card Tier) Health and Max Health **[{100 * (player_card.focus_count * player_card.card_tier)}]**"
        if player_card.universe == "Digimon":
            name = "Mega-Digivolution"
            value =f"On Resolve\nIf turn count < 5, Double your Attack and Defense"
        if player_card.universe == "Naruto":
            name = "Hashirama Cells"
            value =f"On Resolve\nHealth for the amount of stored Hashirama Cells**[{player_card.naruto_heal_buff}]**"
        if player_card.universe == "Demon Slayer":
            name = "Total Concentration Constant"
            value =f"On Resolve\nIf your opponents Attack or Defense is greater than yours, they become equal. If yours are equal or better gain Card Level AP **[{player_card.card_lvl}]** of either Stat."
        if player_card.universe == "YuYu Hakusho":
            name = "Spirit Energy"
            value =f"On Resolve\nSet defense to 100 but Double Attack and all Move AP"
        if player_card.universe == "Jujutsu Kaisen":
            if player_card.card_tier >= 10:
                class_ranking = 6
            elif player_card.card_tier in [8,9]:
                class_ranking = 7
            elif player_card.card_tier in [6,7]:
                class_ranking = 8
            elif player_card.card_tier in [4,5]:
                class_ranking = 9
            else:
                class_ranking = 10
            jjk_value = class_ranking - player_card.focus_count
            if class_ranking - player_card.focus_count <= 0:
                jjk_value = 1
            name = "Domain Expansion"
            value =f"On Resolve\nYour opponent must suceed a damage check they have (10 - Class Ranking - Focus Count) [{jjk_value}] turns to complete, each turn they lose 5% Max Health\nOn Failure they `DIE`\nIf your opponent suceeds and their Focus Count is higher than yours,You Lose the same amount of Max Health "
        if player_card.universe == "Overlord":
            name = "Fear"
            value =f"On Resolve\nOpponent is stricken with fear, opponents defense becomes 25 for Card Tier x 1 turns **[{player_card.card_tier * 1}]**"
        if player_card.universe == "One Piece" and player_card.card_tier in crown_utilities.HIGH_TIER_CARDS:
            name = "Conquerors Haki"
            value =f"On Resolve\nOpponent loses 100 * Card Tier AP **[{100 * player_card.card_tier}]**"
        if player_card.universe == "Souls":
            name = "Phase 2: Enhanced Moveset"
            value =f"On Resolve\nYour `BASIC` attack becomes your `SPECIAL` attack & your `SPECIAL` Attack becomes a 30 ST(Stamina) `ULTIMATE` attack.\n\nNew `SPECIAL` Attack: {player_card.move2_emoji} {player_card.move2} inflicts {player_card.move2_element}\n\nNew `BASIC` Attack: {player_card.move1_emoji} {player_card.move1} inflicts {player_card.move1_element}\n\n**{player_card.summon_name}** used their {player_card.summon_emoji} {player_card.summon_type} ability"
        if player_card.universe == "Fate":
            name = "Command Seal"
            value =f"On Resolve\nStrike with your Ultimate Attack.\nYour Ultimate Attack: {player_card.move3_emoji} {player_card.move3} inflicts {player_card.move3_element}\n**{player_card.move3_element}** : *{crown_utilities.get_element_mapping(player_card.move3_element)}*"
        if player_card.universe == "Bleach":
            name = "Bankai"
            value =f"On Resolve\nDouble your Attack and double the amount of attack gained on Resolve **[{player_card.attack}]**."
        if player_card.universe == "My Hero Academia":
            name = "Quirk Awakening"
            value =f"On Resolve\nGain (Plus Ultra AP  * Focus Count) AP to all Attacks **[{player_card.my_hero_academia_buff}]**"
        if player_card.universe == "Fairy Tail":
            name = "Unison Raid"
            value =f"On Resolve\nStrike with your Special, Ultimate and Summon abilitiy! After this powerful attack you lose 1 run to Recover\n\n`SPECIAL` Attack: {player_card.move2_emoji} {player_card.move2} inflicts {player_card.move2_element}\n\n`ULTIMATE` Attack: {player_card.move3_emoji} {player_card.move3} inflicts {player_card.move3_element}\n\n`SUMMON` Attack: {player_card.summon_emoji} **{player_card.summon_name}** inflicts {player_card.summon_type}"
        if player_card.universe == "Pokemon":
            name = "Evolution"
            value =f"On Resolve\nIncrease defense by Card Tier\nIf turn count > 20 Mega-Evolve and gain 250 * Card Tier Health **[{250 * player_card.card_tier}]**\nIf Turn Count > 30 **Gigantomax** and double it **[{(250 * player_card.card_tier) * 2}]**" 
        if player_card.universe == "That Time I Got Reincarnated as a Slime":
            name = "Skill Evolution"
            value =f"On Resolve\nIncrease `ULTIMATE` AP by total ap of your `BASIC` and `SPECIAL` attack **[{player_card.slime_buff}]** which both become `25` ."
        return name, value
    
    def focus_trait_handler(self, player_card, opponent_card):
        if player_card.universe == "Digimon":
            name = "Digivolve"
            value =f"On Focus\nResolve and increase ATK and DEF **[{100 * player_card.card_tier}]**"
        if player_card.universe == "Naruto":
            name = "Substition Jutsu"
            value =f"On Focus\nYou cannot be hit by attacks, convert any attack damage into `Hashirama Cells` **[{player_card.naruto_heal_buff}]**"
        if player_card.universe == "Black Clover":
            name = "Mana Zone"
            value =f"On Focus\nGain 100 Stamina and increase your AP by (25% * Card Level[Base 50])**[{round((player_card.card_lvl + 49) * .10)}]**"
        if player_card.universe == "Solo Leveling":
            name = "Rulers Authority"
            value =f"On Focus\nOpponent loses (40 + Turn Count) * Card Tier Defense **[{(40 + self.turn_total) * player_card.card_tier}]**"
        if player_card.universe == "One Punch Man":
            name = "Hero Rankings & Monster Threat Levels"
            value =f"On Focus\n\n**Heroes**: Gain 15 * Hero Card Tier AP **[{15 * player_card.card_tier}]**\n\n**Monsters**: Gain 30 * Monster Card Tier **[{30 * player_card.card_tier}]**"
        if player_card.universe == "Jujutsu Kaisen":
            name = "Cursed Energy"
            value =f"After Focus\nYour next attack is a **Critical Strike**!"
        if player_card.universe == "One Piece" and (player_card.card_tier in crown_utilities.MID_TIER_CARDS or player_card.card_tier in crown_utilities.HIGH_TIER_CARDS):
            name = "Armament Haki"
            value =f"On Focus\nDouble Attack and Defense gained during Focus"
        if player_card.universe == "Overlord":
            name = "Fear Aura"
            value =f"On Focus\nOpponent loses Card Tier * 20 AP **[{player_card.card_tier * 20}]**." 
        if player_card.universe == "Fairy Tail":
            name = "Concentration"
            value =f"On Focus\nGain 15 * Card tier * Focus Count AP **[{(15 * player_card.tier) * (player_card.focus_count + 1)}]**." 
        if player_card.universe == "That Time I Got Reincarnated as a Slime":
            o_beezlebub_value = round(opponent_card.attack * (((player_card.tier) / 100 ) * (player_card.focus_count + 1)))
            d_beezlebub_value = round(opponent_card.defense * (((player_card.tier) / 100 ) * (player_card.focus_count + 1)))
            name = "Beezlebuth"
            value =f"On Focus\nSteal (Card Tier * Focus Count)% Attack **[{o_beezlebub_value}]** and Defense **[{d_beezlebub_value}]** from your opponent." 
        
        return name, value
    
    def opponent_focus_trait_handler(self, player_card, opponent_card):
        """
        Handle the opponent focus trait for the player's card.

        Args:
            player_card (Card): The player's card.
            opponent_card (Card): The opponent's card.

        Returns:
            tuple: A tuple containing the name and value of the trait.

        Raises:
            None

        """
        name = False
        value = False
        if opponent_card.universe == "7ds":
            fortitude = round(opponent_card.health * .1)
            if fortitude <= 100:
                fortitude = 100
            attack_calculation = round((.10 * opponent_card.attack))
            defense_calculation = round((.10 * opponent_card.defense))
            f_attack_calculation = round((fortitude * (opponent_card.tier / 10)) + (.05 * opponent_card.attack))
            f_defense_calculation = round((fortitude * (opponent_card.tier / 10)) + (.05 * opponent_card.defense))
            name = "Increase Power & Power of Friendship"
            value = f"On Opponent Focus:\n**Increase Power**: Gain 10% Attack and Defense and 60 Stamina [+🗡️{attack_calculation}| +🛡️{defense_calculation}]\n\n**Power of Friendship**: On Opponent Focus your Summon Rest, Summoning amplifies Increase Power into a Focus Buff[+🗡️{f_attack_calculation}| +🛡️{f_defense_calculation}]"
        if opponent_card.universe == "One Punch Man":
            name = "Hero Reinforcements & Monster Rejuvination"
            value = f"On Opponent Focus:\n\n**Heroes**: gain 50 * Opponent Card Tier Health and Max Health **[{50 * player_card.card_tier}]**\n\n**Monsters**: Gain 25 * Monster Card Tier Health and Max Health **[{25 * opponent_card.card_tier}]**"
        if opponent_card.universe == "Souls":
            name = "Phase 1: Combo Recognition"
            value = f"On Opponent Focus:\nGain (10 * Card Tier) + Turn Count Attack **[{10 * opponent_card.card_tier + self.turn_total}]**"
        return name, value

    def starting_trait_handler(self, player_card, opponent_card):
        if player_card.universe == "Death Note":
            name = "Death Note"
            value =f"On Turn 50\nYour opponent **[{opponent_card.name}]** will have a heart attack and `DIE`"
        if player_card.universe == "One Piece":
            name = "Observation Haki"
            value =f"Reduce incoming damage by 40% until your first focus"
        if player_card.universe == "Chainsawman":
            name = "Fearful"
            value =f"Strong Fear Affliction\n\nThe Fear enhancer does not sacrifice Health"
        if player_card.universe == "Demon Slayer":
            name = "Total Concentration Breathing"
            value =f"Gain 40% of your opponents base max health at the start of battle **[{round(.40 * opponent_card.max_base_health)}]**"
        return name, value
    
    def death_trait_handler(self, player_card):
        if player_card.universe == "Dragon Ball Z":
            name = "Final Stand"
            value =f"On Death\n\nRevive and heal for 75% of your Attack and Defense [{.75 * (player_card.attack + player_card.defense)}]"
        if player_card.universe == "Souls":
            name = "Phase 3: Enhanced Aggresssion"
            value =f"After Resolve\n\nIf health below 40% each attack double strikes with your old Basic Attack\n\n`Phase 3` Attack: {crown_utilities.set_emoji(self.move_souls_element)} {player_card.move_souls} inflicts {player_card.move_souls_element}"
        if player_card.universe == "Chainsawman":
            name = "Devilization"
            value =f"When Health <= 50%\n\nDouble your Attack, Defense Max Health."
        return name, value
    


    def next_turn(self):
        if self.is_co_op_mode:
            if self.is_turn == 3:
                self.is_turn = 0
            else:
                self.is_turn += 1
        else:
            self.is_turn = (self.is_turn + 1) % 2


    def repeat_turn(self):
        self.is_turn = self.is_turn


    def previous_turn(self):
        if self.is_co_op_mode:
            if self.is_turn == 3:
                self.is_turn = 2
            elif self.is_turn == 2:
                self.is_turn = 1
            elif self.is_turn == 1:
                self.is_turn = 0
        else:
            self.is_turn = int(not self.is_turn)


    def get_co_op_bonuses(self, player1, player2):
        if self.is_tales_game_mode or self.is_dungeon_game_mode:
            if player1.guild == player2.guild and player1.guild != 'PCG':
                self.are_teammates = True
                self.co_op_stat_bonus = 50
            if player1.family == player2.family and player1.family != 'PCG':
                self.are_family_members=True
                self.co_op_health_bonus=100
            
            if self.are_teammates:
                bonus_message = f":checkered_flag:**{player1.guild}:** 🗡️**+{self.co_op_stat_bonus}** 🛡️**+{self.co_op_stat_bonus}**"
                if self.are_family_members:
                    bonus_message = f"👨‍👩‍👧‍👦**{player1.family}:** ❤️**+{self.co_op_health_bonus}**\n:checkered_flag:**{player1.guild}:**🗡️**+{self.co_op_stat_bonus}** 🛡️**+{self.co_op_stat_bonus}**"
            elif self.are_family_members:
                    bonus_message = f"👨‍👩‍👧‍👦**{player1.family}:** ❤️**+{self.co_op_health_bonus}**"
            else:
                bonus_message = f"Join a Guild or Create a Family for Coop Bonuses!"

            return bonus_message
    

    async def set_boss_win(self, player1, boss_card, companion=None):
        query = {'DISNAME': player1.disname} 
        fight_query = {'$set' : {'BOSS_FOUGHT' : True}}
        resp = db.updateUserNoFilter(query, fight_query)
        if boss_card.name not in player1.boss_wins:
            if self.is_hard_difficulty:
                await crown_utilities.bless(5000000, player1.did)
            else:
                await crown_utilities.bless(15000000, player1.did)
            if self.is_co_op_mode:
                if self.is_hard_difficulty:
                    await crown_utilities.bless(5000000, companion.did)
                else:
                    await crown_utilities.bless(15000000, companion.did)
            new_query = {'$addToSet': {'BOSS_WINS': boss_card.name}}
            resp = db.updateUserNoFilter(query, new_query)


    async def set_pvp_win_loss(self, your_player_id, opponent_player_id):
        await crown_utilities.bless(10000, your_player_id)

        player1_query = {'DID': your_player_id}
        win_value = {"$inc": {"PVP_WINS" : 1}}
        win_update = db.updateUserNoFilter(player1_query, win_value)

        loss_value = {"$inc": {"PVP_LOSS" : 1}}
        player2_query = {'DID': opponent_player_id}
        loss_update = db.updateUserNoFilter(player2_query, loss_value)


    async def save_abyss_win(self, user, player, player1_card):
        bless_amount = 100000 + (10000 * int(self.abyss_floor))
        await crown_utilities.bless(bless_amount, player.did)
        new_level = int(self.abyss_floor) + 1
        response = db.updateUserNoFilter({'DID': player.did}, {'$set': {'LEVEL': new_level}})
        cardlogger = await crown_utilities.cardlevel(user, "Purchase")


    def get_most_focused(self, player_card, opponent_card, companion_card=None):
        value = ""
        if companion_card:
            if opponent_card.focus_count >= player_card.focus_count:
                if opponent_card.focus_count >= companion_card.focus_count:
                    value=f"{opponent_card.name}"
                else:
                    value=f"{companion_card.name}"
            elif player_card.focus_count >= companion_card.focus_count:
                value=f"{player_card.name}"
            else:
                value=f"{companion_card.name}"
        else:
            if opponent_card.focus_count >= player_card.focus_count:
                value=f"{opponent_card.name}"
            else:
                value=f"{player_card.name}"
        return value
    
    
    def get_most_damage_dealt(self, player_card, opponent_card, companion_card=None):
        value = ""
        if companion_card:
            if opponent_card.damage_dealt >= player_card.damage_dealt:
                if opponent_card.damage_dealt >= companion_card.damage_dealt:
                    value=f"{opponent_card.name}"
                else:
                    value=f"{companion_card.name}"
            elif player_card.damage_dealt >= companion_card.damage_dealt:
                value=f"{player_card.name}"
            else:
                value=f"{companion_card.name}"
        else:
            if opponent_card.damage_dealt >= player_card.damage_dealt:
                value=f"{opponent_card.name}"
            else:
                value=f"{player_card.name}"
        return value
    
    
    def get_most_damage_healed(self, player_card, opponent_card, companion_card=None):
        value = ""
        if companion_card:
            if opponent_card.damage_healed >= player_card.damage_healed:
                if opponent_card.damage_healed >= companion_card.damage_healed:
                    value=f"{opponent_card.name}"
                else:
                    value=f"{companion_card.name}"
            elif player_card.damage_healed >= companion_card.damage_healed:
                value=f"{player_card.name}**"
            else:
                value=f"{companion_card.name}"
        else:
            if opponent_card.damage_healed >= player_card.damage_healed:
                value=f"{opponent_card.name}"
            else:
                value=f"{player_card.name}"
        return value
        
        
    async def explore_embed(self, ctx, winner, winner_card, opponent_card):
        talisman_response = crown_utilities.decrease_talisman_count(winner.did, winner.equipped_talisman)
        if self.player1_wins:
            if self.explore_type == "glory":
                bounty_amount = self.bounty * 2
                await crown_utilities.bless(bounty_amount, winner.did)
                opponent_card.card_lvl = 100
                winner.save_card(opponent_card)
                drop_response = f"You won 🎴 {opponent_card.name}!"
            
                message = f"VICTORY\n🪙 {'{:,}'.format(bounty_amount)} Bounty Received!\nThe game lasted {self.turn_total} rounds.\n\n{drop_response}"
            if self.explore_type == "gold":
                await crown_utilities.bless(self.bounty, winner.did)
                message = f"VICTORY\n🪙 {'{:,}'.format(self.bounty)} Bounty Received!\nThe game lasted {self.turn_total} rounds."
            
            if winner.association != "PCG":
                await crown_utilities.blessguild(250, winner.association)

            if winner.guild != "PCG":
                await crown_utilities.bless(250, winner.did)
                await crown_utilities.blessteam(250, winner.guild)
                await crown_utilities.teamwin(winner.guild)

        else:
            if self.explore_type == "glory":
                await crown_utilities.curse(1000, winner.did)
            
            message = f"YOU LOSE!\nThe game lasted {self.turn_total} rounds."

        embedVar = Embed(title=f"{message}", color=0x1abc9c)
        embedVar.set_footer(text=f"{self.get_previous_moves_embed()}")
        
        f_message = self.get_most_focused(winner_card, opponent_card)
        embedVar.add_field(name=f"🌀 | Focus Count",
                        value=f"**{opponent_card.name}**: {opponent_card.focus_count}\n**{winner_card.name}**: {winner_card.focus_count}")
        #Most Damage Dealth
        d_message = self.get_most_damage_dealt(winner_card, opponent_card)
        embedVar.add_field(name=f"💥 | Damage Dealt",
                        value=f"**{opponent_card.name}**: {opponent_card.damage_dealt}\n**{winner_card.name}**: {winner_card.damage_dealt}")
        #Most Healed
        h_message = self.get_most_damage_healed(winner_card, opponent_card)
        embedVar.add_field(name=f"❤️‍🩹 | Healing",
                        value=f"**{opponent_card.name}**: {opponent_card.damage_healed}\n**{winner_card.name}**: {winner_card.damage_healed}")
        
        return embedVar



    async def get_non_drop_rewards(self, player):
        reward_data = {}

        if player.rift == 1:
            rift_response = db.updateUserNoFilter({'DID': str(player.did)}, {'$set': {'RIFT': 0}})

        if player.family != "PCG":
            family_bank = await crown_utilities.blessfamily(self.fam_reward_amount, player.family)
            reward_data['FAMILY_BANK'] = family_bank
            
        if player.guild != "PCG":
            team_bank = await crown_utilities.blessteam(self.bank_amount, player.guild)
            reward_data['TEAM_BANK'] = team_bank
            
        random_element = crown_utilities.select_random_element(self.difficulty, self.mode)
        essence = crown_utilities.inc_essence(player.did, random_element["ELEMENT"], random_element["ESSENCE"])
        reward_data['RANDOM_ELEMENT'] = random_element['ESSENCE']
        reward_data['ESSENCE'] = essence

        return reward_data
    

    async def get_rematch_buttons(self, player):
        try:
            play_again_buttons = [
                Button(
                    style=ButtonStyle.BLUE,
                    label="Start Over",
                    custom_id="Yes"
                ),
                Button(
                    style=ButtonStyle.RED,
                    label="End",
                    custom_id="No"
                )
            ]
            
            self.rematch_buff = False
            if player.guild != 'PCG':
                team_info = db.queryTeam({'TEAM_NAME': str(player.guild.lower())})
                guild_buff_info = team_info['ACTIVE_GUILD_BUFF']
                if guild_buff_info == 'Rematch':
                    self.rematch_buff =True
            
            if self.rematch_buff: #rematch update
                play_again_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=f"Guild Rematches Available!",
                        custom_id="grematch"
                    )
                )
            
            elif player.retries >= 1:
                play_again_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=f"{player.retries} Rematches Available!",
                        custom_id="rematch"
                    )
                )

            else:
                self.rematch_buff = False

            return play_again_buttons
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


    async def configure_battle_players(self, ctx, player2=None, player3=None):
        try:
            opponent_talisman_emoji = ""
            self.configure_player_1()

            if self.is_pvp_game_mode:
                self.configure_player_2(player2)
            
            if self.is_raid_game_mode:
                self.configure_raid_opponent(player2)

            if self.is_ai_opponent and not self.is_raid_game_mode:
                await self.configure_ai_opponent_1(ctx)
                if self.is_co_op_mode or self.is_duo_mode:
                    self.configure_partner_1(player3)
                
        except Exception as ex:
            print(ex)


    def configure_player_1(self):
        try:
            self.player1 = crown_utilities.create_player_from_data(db.queryUser({'DID': str(self.player1.did)}))
            self.player1.get_battle_ready()
            self.player1_card = crown_utilities.create_card_from_data(self.player1._equipped_card_data, self._ai_is_boss)
            self.player1_title = crown_utilities.create_title_from_data(self.player1._equipped_title_data)
            self.player1_arm = crown_utilities.create_arm_from_data(self.player1._equipped_arm_data)
            self.player1.getsummon_ready(self.player1_card)
            self.player1_arm.set_durability(self.player1.equipped_arm, self.player1.arms)
            self.player1_card.set_card_level_buffs(self.player1.card_levels)
            self.player1_card.set_arm_config(self.player1_arm.passive_type, self.player1_arm.name, self.player1_arm.passive_value, self.player1_arm.element)
            self.player1_card.set_affinity_message()
            self.player1.get_talisman_ready(self.player1_card)
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
            return


    def configure_player_2(self, player2):
        try:
            opponent_talisman_emoji = ""
            self.player2 = player2
            self.player2.get_battle_ready()
            self.player2_card = crown_utilities.create_card_from_data(self.player2._equipped_card_data, self._ai_is_boss)
            self.player2_title = crown_utilities.create_title_from_data(self.player2._equipped_title_data)
            self.player2_arm = crown_utilities.create_arm_from_data(self.player2._equipped_arm_data)
            self.opponent_talisman_emoji = crown_utilities.set_emoji(self.player2.equipped_talisman)
            self.player2.getsummon_ready(self.player2_card)
            self.player2_arm.set_durability(self.player2.equipped_arm, self.player2.arms)
            self.player2_card.set_card_level_buffs(self.player2.card_levels)
            self.player2_card.set_arm_config(self.player2_arm.passive_type, self.player2_arm.name, self.player2_arm.passive_value, self.player2_arm.element)
            set_solo_leveling_config(self.player2_card, self.player1_card.shield_active, self.player1_card._shield_value, self.player1_card.barrier_active, self.player1_card._barrier_value, self.player1_card.parry_active, self.player1_card._parry_value)
            self.player2_card.set_affinity_message()
            self.player2.get_talisman_ready(self.player2_card)
            set_solo_leveling_config(self.player1_card, self.player2_card.shield_active, self.player2_card._shield_value, self.player2_card.barrier_active, self.player2_card._barrier_value, self.player2_card.parry_active, self.player2_card._parry_value)
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
            return


    def configure_raid_opponent(self, player2):
        self.player2 = player2
        self.player2.get_battle_ready()
        self.player2_card = crown_utilities.create_card_from_data(self.player2._equipped_card_data, self._ai_is_boss)
        self.player2_title = crown_utilities.create_title_from_data(self.player2._equipped_title_data)
        self.player2_arm = crown_utilities.create_arm_from_data(self.player2._equipped_arm_data)
        opponent_talisman_emoji = crown_utilities.set_emoji(self.player2.equipped_talisman)
        self.player2.getsummon_ready(self.player2_card)
        self.player2_arm.set_durability(self.player2.equipped_arm, self.player2.arms)
        self.player2_card.set_card_level_buffs(self.player2.card_levels)
        self.player2_card.set_arm_config(self.player2_arm.passive_type, self.player2_arm.name, self.player2_arm.passive_value, self.player2_arm.element)
        # player2_card.set_solo_leveling_config(player1_card.shield_active, player1_card._shield_value, player1_card.barrier_active, player1_card._barrier_value, player1_card.parry_active, player1_card._parry_value)
        self.player2_card.set_affinity_message()
        self.player2_card.set_raid_defense_buff(self._hall_defense)
        self.player2.get_talisman_ready(self.player2_card)


    def configure_partner_1(self, partner1):
        try:
            self.player3 = partner1
            self.player3.get_battle_ready()
            self.player3_card = crown_utilities.create_card_from_data(self.player3._equipped_card_data, self._ai_is_boss)
            self.player3_title = crown_utilities.create_title_from_data(self.player3._equipped_title_data)
            self.player3_arm = crown_utilities.create_arm_from_data(self.player3._equipped_arm_data)
            self.player3_talisman_emoji = crown_utilities.set_emoji(self.player3.equipped_talisman)
            self.player3.getsummon_ready(self.player3_card)
            self.player3_arm.set_durability(self.player3.equipped_arm, self.player3.arms)
            self.player3_card.set_card_level_buffs(self.player3.card_levels)
            self.player3_card.set_arm_config(self.player3_arm.passive_type, self.player3_arm.name, self.player3_arm.passive_value, self.player3_arm.element)
            # player3_card.set_solo_leveling_config(player1_card.shield_active, player1_card._shield_value, player1_card.barrier_active, player1_card._barrier_value, player1_card.parry_active, player1_card._parry_value)
            self.player3_card.set_affinity_message()
            self.player3.get_talisman_ready(self.player3_card)
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
            return


    async def configure_ai_opponent_1(self, ctx):
        try:
            if self.is_scenario_game_mode:
                self.is_tales_game_mode = False
            if self.is_explore_game_mode:
                self.battle_mode = "Explore"
                self.player2_card = self._ai_opponent_card_data
                self.get_aisummon_ready(self.player2_card)
                self.player2_title = crown_utilities.create_title_from_data(db.queryTitle({"TITLE": self._ai_opponent_title_data}))
                self.player2_arm = crown_utilities.create_arm_from_data(db.queryArm({"ARM": self._ai_opponent_arm_data}))
                self.player2_card.set_talisman(self)
                opponent_talisman_emoji = ""
                self.player2_card.set_arm_config(self.player2_arm.passive_type, self.player2_arm.name, self.player2_arm.passive_value, self.player2_arm.element)
                self.player2_card.set_affinity_message()
                self.player2_card.get_tactics(self)
                return

            await self.get_ai_battle_ready(self.player1_card.card_lvl)
            self.player2_card = crown_utilities.create_card_from_data(self._ai_opponent_card_data, self._ai_is_boss)
            self.get_aisummon_ready(self.player2_card)
            self.player2_card.set_ai_card_buffs(self._ai_opponent_card_lvl, self.stat_buff, self.stat_debuff, self.health_buff, self.health_debuff, self.ap_buff, self.ap_debuff, self.player1.prestige, self.player1.rebirth, self.mode)
            if self.abyss_player_card_tier_is_banned:
                await ctx.send(f"Tier {str(self.player2_card.tier)} cards are banned on Floor {str(self.abyss_floor)} of the abyss. Please try again with another card.")
                return
            self.player2_title = crown_utilities.create_title_from_data(self._ai_opponent_title_data)
            self.player2_arm = crown_utilities.create_arm_from_data(self._ai_opponent_arm_data)
            self.player2_card.set_talisman(self)
            opponent_talisman_emoji = ""
            self.player2_card.set_arm_config(self.player2_arm.passive_type, self.player2_arm.name, self.player2_arm.passive_value, self.player2_arm.element)
            self.player2_card.set_affinity_message()
            self.player2_card.get_tactics(self)
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
            return


    async def pvp_victory_embed(self, winner, winner_card, winner_arm, winner_title, loser, loser_card):
        wintime = datetime.datetime.now()
        starttime = datetime.datetime.now()
        gameClock = crown_utilities.getTime(starttime.hour, starttime.minute, starttime.second,
                                            wintime.hour, wintime.minute, wintime.second)

        await self.set_pvp_win_loss(winner.did, loser.did)
        await self.manage_associations_and_guilds(winner, loser)

        match = await crown_utilities.savematch(winner.did, winner_card.name, winner_card.path, winner_title.name,
                                                winner_arm.name, "N/A", "PVP", False)
        embedVar = self.create_embed_var(winner, winner_card, loser, loser_card, gameClock)
        return embedVar


    async def you_lose_embed(self, player_card, opponent_card, companion_card=None):
        wintime = datetime.datetime.now()
        starttime = datetime.datetime.now()
        gameClock = crown_utilities.getTime(starttime.hour, starttime.minute, starttime.second,
                                            wintime.hour, wintime.minute, wintime.second)

        embedVar = await self.create_loss_embed_var(player_card, opponent_card, companion_card, gameClock)
        return embedVar


    async def manage_associations_and_guilds(self, winner, loser):
        if winner.association != "PCG":
            await crown_utilities.blessguild(250, winner.association)
        if winner.guild != "PCG":
            await self.bless_winner_guild(winner)
        if loser.association != "PCG":
            await crown_utilities.curseguild(100, loser.association)
        if loser.guild != "PCG":
            await self.curse_loser_guild(loser)


    async def bless_winner_guild(self, winner):
        await crown_utilities.bless(250, winner.did)
        await crown_utilities.blessteam(250, winner.guild)
        await crown_utilities.teamwin(winner.guild)


    async def curse_loser_guild(self, loser):
        await crown_utilities.curse(25, loser.did)
        await crown_utilities.curseteam(50, loser.guild)
        await crown_utilities.teamloss(loser.guild)


    def create_embed_var(self, winner, winner_card, loser, loser_card, gameClock):
        embedVar = self.embed_title(winner, winner_card)
        embedVar.set_footer(text=f"{self.get_previous_moves_embed()}"f"\n{self.format_game_clock(gameClock)}")
        self.add_stat_fields_to_embed(embedVar, winner_card, loser_card)
        return embedVar


    async def create_loss_embed_var(self, player_card, opponent_card, companion_card, gameClock):
        if self.is_raid_game_mode:
            embedVar = Embed(title=f"🛡️ **{opponent_card.name}** defended the {self._association_name}\nMatch concluded in {self.turn_total} turns", color=0x1abc9c)
        else:
            embedVar = Embed(title=f"💀 Try Again", color=0xe91e63)


        # Define a list of milestones to check
        milestones = [
            (self.player1, self.battle_mode, 1, self.selected_universe),
            (self.player1, self.player1_card.move1_element, self.player1_card.move1_damage_dealt, self.selected_universe),
            (self.player1, self.player1_card.move2_element, self.player1_card.move2_damage_dealt, self.selected_universe),
            (self.player1, self.player1_card.move3_element, self.player1_card.move3_damage_dealt, self.selected_universe),
        ]

        # Check milestones and add messages to the embed
        for milestone in milestones:
            milestone_messages = await Quests.milestone_check(*milestone)
            if milestone_messages:
                for message in milestone_messages:
                    embedVar.add_field(name="🏆 Milestone", value=message)


        embedVar.set_footer(text=f"{self.get_previous_moves_embed()}"f"\n{self.format_game_clock(gameClock)}")
        self.add_stat_fields_to_embed(embedVar, player_card, opponent_card, companion_card)
        return embedVar


    def embed_title(self, winner, winner_card):
        victory_message = f"⚡ {winner_card.name} WINS!"
        victory_description = f"Match concluded in {self.turn_total} turns."
        
        if self.is_tutorial_game_mode:
            victory_message = f"⚡ TUTORIAL VICTORY"
            victory_description = f"_What is Next?_\nUse **/daily** to earn your daily rewards and quest!\nTry the other **/play** games modes!\n\nUse **/blacksmith** to maintain your Cards and equipment!\n"
        
        elif self.is_pvp_game_mode:
            victory_message = f"⚡ {winner_card.name} WINS!"
            victory_description = f"Match concluded in {self.turn_total} turns."
        
        embed = Embed(title=f"{victory_message}\n{victory_description}", color=0xe91e63)
        embed.set_footer(text=f"{self.get_previous_moves_embed()}")
        return embed


    def add_stat_fields_to_embed(self, embedVar, winner_card, opponent_card, companion_card=None):
        # for name, action in zip(['🌀 | Focus Count', '💥 | Damage Dealt', '❤️‍🩹 | Healing'],
        #                         [self.get_most_focused, self.get_most_damage_dealt, self.get_most_damage_healed]):
        #     values = "\n".join([f"**{card.name}**: {action(player_card, opponent_card)}" for card, player_card, opponent_card in zip(cards, player_cards, opponent_cards)])
        #     embedVar.add_field(name=name, value=values)

        f_message = self.get_most_focused(winner_card, opponent_card)
        embedVar.add_field(name=f"🌀 | Focus Count",
                        value=f"**{opponent_card.name}**: {opponent_card.focus_count}\n**{winner_card.name}**: {winner_card.focus_count}")
        #Most Damage Dealth
        d_message = self.get_most_damage_dealt(winner_card, opponent_card)
        embedVar.add_field(name=f"💥 | Damage Dealt",
                        value=f"**{opponent_card.name}**: {opponent_card.damage_dealt}\n**{winner_card.name}**: {winner_card.damage_dealt}")
        #Most Healed
        h_message = self.get_most_damage_healed(winner_card, opponent_card)
        embedVar.add_field(name=f"❤️‍🩹 | Healing",
                        value=f"**{opponent_card.name}**: {opponent_card.damage_healed}\n**{winner_card.name}**: {winner_card.damage_healed}")
        


    def format_game_clock(self, gameClock):
        if gameClock[0] == 0 and gameClock[1] == 0:
            return f"Battle Time: {gameClock[2]} Seconds."
        elif gameClock[0] == 0:
            return f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds."
        else:
            return f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds."


def ai_enhancer_moves(your_card, opponent_card):
    aiMove = 1
    if your_card.barrier_active:
        aiMove = 4
        if your_card.move4enh in ["RAGE", "BRACE", "GROWTH"]:
            if your_card.card_lvl_ap_buff >= 1000 + your_card.card_lvl:
                aiMove = 0
        elif your_card.move4enh in ['FEAR']:
            if opponent_card.card_lvl_ap_buff <= 0:
                aiMove = 0
        elif your_card.move4enh in crown_utilities.INC_Enhancer_Check: #Ai Inc Check
            if your_card.attack >= 8000 or your_card.defense >=8000:
                if your_card.used_focus and not your_card.used_resolve:
                    aiMove =5
                else:
                    if your_card.stamina >=80 and your_card.used_focus:
                        aiMove = 3
                    elif your_card.stamina>=30 and your_card.used_focus:
                        aiMove = 2
                    else:
                        aiMove = 1
            else:
                aiMove = 4
        elif your_card.move4enh in crown_utilities.DPS_Enhancer_Check: #Ai Steal Check
            if your_card.attack >= 8000 and opponent_card.attack >=100:
                if your_card.used_focus and not your_card.used_resolve:
                    aiMove =5
                else:
                    if your_card.stamina >=80 and your_card.used_focus:
                        aiMove = 3
                    elif your_card.stamina>=30 and your_card.used_focus:
                        aiMove = 2
                    else:
                        aiMove = 1
            elif your_card.defense >= 8000 and opponent_card.defense >=100:
                if your_card.used_focus and not your_card.used_resolve:
                    aiMove =5
                else:
                    if your_card.stamina >=80 and your_card.used_focus:
                        aiMove = 3
                    elif your_card.stamina>=30 and your_card.used_focus:
                        aiMove = 2
                    else:
                        aiMove = 1
            else:
                aiMove = 4
        elif your_card.move4enh in crown_utilities.Sacrifice_Enhancer_Check: #Ai Sacrifice Check
            if your_card.attack >= 8000 or your_card.health <= 1500 or your_card.health <= (.50 * your_card.max_health):
                if your_card.used_focus and not your_card.used_resolve:
                    aiMove =5
                else:
                    if your_card.stamina >=80 and your_card.used_focus:
                        aiMove = 3
                    elif your_card.stamina>=30 and your_card.used_focus:
                        aiMove = 2
                    else:
                        aiMove = 1
            elif your_card.defense >= 8000 or your_card.health <=1500 or your_card.health <= (.50 * your_card.max_health):
                if your_card.used_focus and not your_card.used_resolve:
                    aiMove =5
                else:
                    if your_card.stamina >=80 and your_card.used_focus:
                        aiMove = 3
                    elif your_card.stamina>=30 and your_card.used_focus:
                        aiMove = 2
                    else:
                        aiMove = 1
        else:
            aiMove = 4
        
    elif your_card.move4enh in crown_utilities.Time_Enhancer_Check:
        if your_card.move4enh == "HASTE":
            if opponent_card.stamina <= your_card.stamina:
                aiMove =4
            else:
                if your_card.stamina >=80 and your_card.used_focus:
                    aiMove = 3
                elif your_card.stamina>=30 and your_card.used_focus:
                    aiMove = 2
                else:
                    aiMove = 1
        elif your_card.move4enh == "SLOW":
            if your_card.stamina <= opponent_card.stamina:
                aiMove =4
            else:
                if your_card.stamina >=80 and your_card.used_focus:
                    aiMove = 3
                elif your_card.stamina>=30 and your_card.used_focus:
                    aiMove = 2
                else:
                    aiMove = 1
        else:
            if your_card.used_focus ==False:
                aiMove=4
            else:
                if your_card.move4enh == "BLINK":
                    aiMove =4
                else:
                    if your_card.stamina >=80 and your_card.used_focus:
                        aiMove = 3
                    elif your_card.stamina>=30 and your_card.used_focus:
                        aiMove = 2
                    else:
                        aiMove = 1
    elif your_card.move4enh in crown_utilities.SWITCH_Enhancer_Check:
        if your_card.move4enh == "CONFUSE":
            if opponent_card.defense >= your_card.defense:
                if opponent_card.attack >= your_card.defense:
                    if opponent_card.attack>=opponent_card.defense:
                        aimove =4
                    else:
                        if your_card.stamina >=80 and your_card.used_focus:
                            aiMove = 3
                        elif your_card.stamina>=30 and your_card.used_focus:
                            aiMove = 2
                        else:
                            aiMove = 1
                else:
                    if your_card.stamina >=80 and your_card.used_focus:
                        aiMove = 3
                    elif your_card.stamina>=30 and your_card.used_focus:
                        aiMove = 2
                    else:
                        aiMove = 1
            else:
                if your_card.stamina >=80 and your_card.used_focus:
                    aiMove = 3
                elif your_card.stamina>=30 and your_card.used_focus:
                    aiMove = 2
                else:
                    aiMove = 1
        else:
            if your_card.attack >= 800 and your_card.defense>= 800:
                aiMove = 1
            else:
                aiMove = 4
    elif your_card.move4enh in crown_utilities.Damage_Enhancer_Check or your_card.move4enh in crown_utilities.Turn_Enhancer_Check: #Ai Damage Check
        aiMove = 4
    elif your_card.move4enh in crown_utilities.Gamble_Enhancer_Check: #Ai Gamble and Soul checks
        aiMove =4
    elif your_card.move4enh in crown_utilities.Stamina_Enhancer_Check: #Ai Stamina Check
        if your_card.stamina >= 240:
            if your_card.stamina >=80 and your_card.used_focus:
                aiMove = 3
            elif your_card.stamina>=30 and your_card.used_focus:
                aiMove = 2
            else:
                aiMove = 3
        else:
            aiMove = 4
    elif your_card.move4enh in crown_utilities.TRADE_Enhancer_Check: #Ai Trade Check
        if your_card.defense >= your_card.attack and your_card.defense <= (your_card.attack * 2):
            aiMove = 4
        elif your_card.attack <= (your_card.defense * 2):
            aiMove =4
        else:
            if your_card.stamina >=90 and your_card.used_focus:
                if your_card.defense >= your_card.attack:
                    if your_card.used_focus and not your_card.used_resolve:
                        aiMove =5
                    else:
                        if your_card.stamina >=80 and your_card.used_focus:
                            aiMove = 3
                        elif your_card.stamina>=30 and your_card.used_focus:
                            aiMove = 2
                        else:
                            aiMove = 1
                else:
                    aiMove = 3
            else:
                if your_card.stamina >=80 and your_card.used_focus:
                    aiMove = 3
                elif your_card.stamina>=30 and your_card.used_focus:
                    aiMove = 2
                else:
                    aiMove = 1
    elif your_card.move4enh in crown_utilities.Healer_Enhancer_Check: #Ai Healer Check
        if your_card.health >= your_card.max_health:
            if your_card.stamina >=80 and your_card.used_focus:
                aiMove = 3
            elif your_card.stamina>=30 and your_card.used_focus:
                aiMove = 2
            else:
                aiMove = 1
        else:
            aiMove = 4
    elif your_card.move4enh in crown_utilities.INC_Enhancer_Check: #Ai Inc Check
        if your_card.attack >= 8000 or your_card.defense >=8000:
            if your_card.stamina >=80 and your_card.used_focus:
                aiMove = 3
            elif your_card.stamina>=30 and your_card.used_focus:
                aiMove = 2
            else:
                aiMove = 1
        else:
            aiMove = 4
    elif your_card.move4enh in crown_utilities.DPS_Enhancer_Check: #Ai Steal Check
        if your_card.attack >= 8000 and opponent_card.attack >=100:
            if your_card.stamina >=80 and your_card.used_focus:
                aiMove = 3
            elif your_card.stamina>=30 and your_card.used_focus:
                aiMove = 2
            else:
                aiMove = 1
        elif your_card.defense >= 8000 and opponent_card.defense >=100:
            if your_card.stamina >=80 and your_card.used_focus:
                aiMove = 3
            elif your_card.stamina>=30 and your_card.used_focus:
                aiMove = 2
            else:
                aiMove = 1
        else:
            aiMove = 4
    elif your_card.move4enh in crown_utilities.FORT_Enhancer_Check: #Ai Fort Check
        if (opponent_card.attack<= 50 or your_card.attack >=5000) or your_card.health <= 1000 or your_card.health <= (.66 * your_card.max_health):
            if your_card.stamina >=80 and your_card.used_focus:
                aiMove = 3
            elif your_card.stamina>=30 and your_card.used_focus:
                aiMove = 2
            else:
                aiMove = 1
        elif (opponent_card.defense <=50 or your_card.defense >= 5000) or your_card.health <= 1000 or your_card.health <= (.66 * your_card.max_health):
            if your_card.stamina >=80 and your_card.used_focus:
                aiMove = 3
            elif your_card.stamina>=30 and your_card.used_focus:
                aiMove = 2
            else:
                aiMove = 1
        else:
            aiMove = 4
    elif your_card.move4enh in crown_utilities.Sacrifice_Enhancer_Check: #Ai Sacrifice Check
        if your_card.attack >= 5000 or your_card.health <= 1000 or your_card.health <= (.75 * your_card.max_health):
            if your_card.used_focus and not your_card.used_resolve:
                aiMove =5
            else:
                if your_card.stamina >=80 and your_card.used_focus:
                    aiMove = 3
                elif your_card.stamina>=30 and your_card.used_focus:
                    aiMove = 2
                else:
                    aiMove = 1
        elif your_card.defense >= 5000 or your_card.health <=1000 or your_card.health <= (.75 * your_card.max_health):
            if your_card.used_focus and not your_card.used_resolve:
                aiMove =5
            else:
                if your_card.stamina >=80 and your_card.used_focus:
                    aiMove = 3
                elif your_card.stamina>=30 and your_card.used_focus:
                    aiMove = 2
                else:
                    aiMove = 1
        else:
            aiMove = 4
    else:
        aiMove = 4 #Block or Enhance
        
    #Killing Blow Checks
    if opponent_card.health <= 500:
        if your_card.stamina >= 80:
            aiMove =3
        elif your_card.stamina >= 30:
            aiMove=2
        elif your_card.stamina >= 20:
            if your_card.move4enh == "LIFE" or your_card.move4enh in crown_utilities.Damage_Enhancer_Check:
                aiMove = 4
            else:
                aiMove = 1
        else:
            aiMove = 1
            
        
    return aiMove


