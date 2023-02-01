import db
import crown_utilities
import discord
import textwrap

class Battle:
    def __init__(self, mode, _player):
        self.player = _player

        self.mode = mode
        self._is_tales = False
        self._is_dungeon = False
        self._is_explore = False
        self._is_abyss = False
        self._is_boss = False
        self._is_tutorial = False
        self._is_raid = False
        self._is_scenario = False
        self._is_pvp_match = False
        self._is_available = True
        self._is_corrupted = False
        self._can_save_match = False

        self._is_auto_battle = False

        self._list_of_opponents = []
        self._total_enemies = 0
        self._currentopponent = 0
        self._match_lineup = ""
        self._is_turn = 0
        self._turn_total = 0
        self._max_turns_allowed = 250
        self.previous_moves = []
        self.previous_moves_len = 0

        self._selected_universe = ""
        self._selected_universe_data = ""

        self._is_co_op = False
        self._is_duo = False
        self.is_ai_opponent = False
        self._ai_title = ""
        self._ai_arm = ""
        self._ai_summon = ""

        self._ai_opponent_card_data = ""
        self._ai_opponent_title_data = ""
        self._ai_opponent_arm_data = ""
        self._ai_opponent_summon_data = ""
        self._ai_opponent_summon_power = 0
        self._ai_opponent_summon_bond = 0
        self._ai_opponent_summon_lvl = 0
        self._ai_opponent_summon_type = ""
        self._ai_opponent_summon_name = ""
        self._ai_opponent_summon_universe = ""
        self._ai_opponent_summon_ability_name = ""
        self._ai_opponent_summon_image = ""

        self.difficulty = _player.difficulty
        self._is_easy = False
        self._is_hard = False
        self._is_normal = False

        self.health_buff = 0
        self.health_debuff = 0
        self.stat_buff = 0
        self.stat_debuff = 0
        self.ap_buff = 0
        self.ap_debuff = 0

        # Universal Elemetal Buffs
        self._wind_buff = 0

        self._ai_opponent_card_lvl = 0
        self._ai_opponent_summon_bond = 0
        self._ai_can_use_summon = False

        self.scaling_stat = 0
        self._boss_fought_already = False

        self._completed_tales = self.player.completed_tales
        self._completed_dungeons = self.player.completed_dungeons
        self._player_association = ""
        self._name_of_boss = ""
        self._ai_opponent_card_lvl = 0

        # Messages
        self.abyss_message = ""
        self.starting_match_title = f"✅ Start Battle!  ({self._currentopponent + 1}/{self._total_enemies})"

        # Abyss / Scenario / Explore Config
        self.abyss_floor = ""
        self.abyss_card_to_earn = ""
        self.abyss_banned_card_tiers = ""
        self.abyss_player_card_tier_is_banned = False
        self.scenario_easy_drops = []
        self.scenario_normal_drops = []
        self.scenario_hard_drops = []
        self.explore_type = ""
        self.explore_card = ""

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
        self.tutorial_message = ""

        self.game_over = False
        self.player_1_wins = False
        self.player_2_wins = False


        if self.mode not in crown_utilities.PVP_M:
            self._is_tales = True
            self._total_enemies = 1

        if self.mode in crown_utilities.AUTO_BATTLE_M:
            self._is_auto_battle = True
            self.is_ai_opponent = True

        if self.mode in crown_utilities.AI_CO_OP_M:
            self._is_duo = True
            self.is_ai_opponent = True
            self.starting_match_title = f"Duo Battle! ({self._currentopponent + 1}/{self._total_enemies})"

        if self.mode in crown_utilities.CO_OP_M:
            self._is_co_op = True
            self.is_ai_opponent = True
            self.starting_match_title = f"Co-op Battle! ({self._currentopponent + 1}/{self._total_enemies})"

        if self.mode in crown_utilities.RAID_M:
            self._is_raid = True
            self.is_ai_opponent = True
            self.starting_match_title = f"Raid Battle!"

        if self.mode in crown_utilities.TALE_M:
            self._is_tales = True
            self.is_ai_opponent = True
            self._ai_opponent_summon_lvl = 5
            self._ai_opponent_summon_bond = 1
            self._ai_opponent_card_lvl = 30

        
        if self.mode in crown_utilities.DUNGEON_M:
            self._is_dungeon = True
            self.is_ai_opponent = True
            self._ai_opponent_summon_lvl = 10
            self._ai_opponent_summon_bond = 3
            self._ai_opponent_card_lvl = 400
            self.health_buff = self.health_buff + 2000
            self.stat_buff = self.stat_buff + 100
            self.ap_buff = self.ap_buff + 80


        if self.mode in crown_utilities.BOSS_M:
            self._is_boss = True
            self.is_ai_opponent = True
            self._ai_opponent_summon_lvl = 15
            self._ai_opponent_summon_bond = 4
            self._ai_opponent_card_lvl = 1000
            self.health_buff = self.health_buff + 5000
            self.stat_buff = self.stat_buff + 250
            self.ap_buff = self.ap_buff + 250
            self._total_enemies = 1
            self.starting_match_title = "👿 BOSS BATTLE!"


        if self.mode == crown_utilities.ABYSS:
            self._is_abyss = True
            self.is_ai_opponent = True

        if self.mode == crown_utilities.SCENARIO:
            self._is_scenario = True
            self.is_ai_opponent = True

        if self.mode == crown_utilities.EXPLORE:
            self._is_explore = True
            self.is_ai_opponent = True
            self._total_enemies = 1
            self.starting_match_title = f"{self.explore_type.title()} Battle!"

        if self.difficulty == "EASY":
            self._is_easy = True
            self._is_easy = True
            self.health_debuff = self.health_debuff + 500
            self.stat_debuff = self.stat_debuff + 100
            self.ap_debuff = self.ap_debuff + 15

        
        if self.difficulty == "NORMAL":
            self._is_normal = True
        
        if self.difficulty == "HARD":
            self._is_hard = True
            self.health_buff = self.health_buff + 3000
            self.stat_buff = self.stat_buff + 200
            self.ap_buff = self.ap_buff + 150

        if self.is_ai_opponent:
            self._ai_can_use_summon = True

        if self._is_tutorial:
            self.starting_match_title = "Click Start Match to Begin the Tutorial!"
        

        
    def set_universe_selection_config(self, universe_selection):
        if universe_selection:
            self.selected_universe = universe_selection['SELECTED_UNIVERSE']
            self._selected_universe_data = universe_selection['UNIVERSE_DATA']
            self.crestlist = universe_selection['CREST_LIST']
            self.crestsearch = universe_selection['CREST_SEARCH']
            self._currentopponent =  universe_selection['CURRENTOPPONENT']

            if self.mode in crown_utilities.DUNGEON_M:
                self._list_of_opponents = self._selected_universe_data['DUNGEONS']
                self._total_enemies = len(self._list_of_opponents)
            if self.mode in crown_utilities.TALE_M:
                self._list_of_opponents = self._selected_universe_data['CROWN_TALES']
                self._total_enemies = len(self._list_of_opponents)

            if self.mode in crown_utilities.BOSS_M:
                self._name_of_boss = universe_selection['BOSS_NAME']
                self._player_association = universe_selection['OGUILD']
                if self.player.boss_fought:
                    self._boss_fought_already = True

            if self.crestsearch:
                self._player_association = universe_selection['OGUILD']
            else:
                self._player_association = "PCG"

            self.starting_match_title = f"✅ Start Battle!  ({self._currentopponent + 1}/{self._total_enemies})"



    def set_abyss_config(self):
        if self._is_abyss:
            try:
                if self._is_easy:
                    self.abyss_message = "The Abyss is unavailable on Easy self.mode! Use /difficulty to change your difficulty setting."
                    return

                checks = db.queryCard({'NAME': self.player.equipped_card})
                abyss = db.queryAbyss({'FLOOR': self.player.level})

                if not abyss:
                    self.abyss_message = "You have climbed out of :new_moon: **The Abyss**! Use /exchange to **Prestige**!"
                    return


                if abyss['FLOOR'] in crown_utilities.ABYSS_REWARD_FLOORS:
                    unlockable_message = f"⭐ Drops on this Floor\nUnlockable Card: **{card_to_earn}**\nUnlockable Title: **{title}**\nUnlockable Arm: **{arm}**\n"
                else:
                    unlockable_message = ""

                self._list_of_opponents = abyss['ENEMIES']
                self._total_enemies = len(self._list_of_opponents)
                self._ai_opponent_card_lvl = int(abyss['SPECIAL_BUFF'])
                self.abyss_floor = abyss['FLOOR']
                self.abyss_card_to_earn = self._total_enemies[-1] 
                self._ai_title = abyss['TITLE']
                self._ai_arm = abyss['ARM']
                self.abyss_banned_card_tiers = abyss['BANNED_TIERS']
                # Convert tiers into strings from ints
                self.abyss_banned_tier_conversion_to_string = [str(tier) for tier in self.abyss_banned_card_tiers]

                if checks['TIER'] in self.abyss_banned_card_tiers:
                    self.abyss_player_card_tier_is_banned = True

                # Configure Embed
                embedVar = discord.Embed(title=f":new_moon: Abyss Floor {self.abyss_floor}  ⚔️{len(self._list_of_opponents)}", description=textwrap.dedent(f"""
                {unlockable_message}
                """))
                if self.abyss_banned_card_tiers:
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

    
    def set_scenario_selection(self):
        try:
            scenarios = db.queryAllScenariosByUniverse(str(self._selected_universe))
            embed_list = []
            for scenario in scenarios:
                if scenario['AVAILABLE']:
                    title = scenario['TITLE']
                    enemies = scenario['ENEMIES']
                    number_of_fights = len(enemies)
                    enemy_level = scenario['ENEMY_LEVEL']
                    scenario_gold = crown_utilities.scenario_gold_drop(enemy_level)
                    universe = scenario['UNIVERSE']
                    scenario_image = scenario['IMAGE']
                    reward_list = []
                    if self._is_easy:
                        rewards = scenario['EASY_DROPS']
                        scenario_gold = round(scenario_gold / 3)
                    if self._is_normal:
                        rewards = scenario['NORMAL_DROPS']
                    if self._is_hard:
                        rewards = scenario['HARD_DROPS']
                        scenario_gold = round(scenario_gold * 3)

                    for reward in rewards:
                        # Add Check for Cards and make Cards available in Easy Drops
                        arm = db.queryArm({"ARM": reward})
                        if arm:
                            arm_name = arm['ARM']
                            element_emoji = crown_utilities.set_emoji(arm['ELEMENT'])
                            arm_passive = arm['ABILITIES'][0]
                            arm_passive_type = list(arm_passive.keys())[0]
                            arm_passive_value = list(arm_passive.values())[0]
                            if arm_passive_type == "SHIELD":
                                reward_list.append(f":globe_with_meridians: {arm_passive_type.title()} **{arm_name}** Shield: Absorbs **{arm_passive_value}** Damage.")
                            elif arm_passive_type == "BARRIER":
                                reward_list.append(f":diamond_shape_with_a_dot_inside:  {arm_passive_type.title()} **{arm_name}** Negates: **{arm_passive_value}** attacks.")
                            elif arm_passive_type == "PARRY":
                                reward_list.append(f":repeat: {arm_passive_type.title()} **{arm_name}** Parry: **{arm_passive_value}** attacks.")
                            elif arm_passive_type == "SIPHON":
                                reward_list.append(f":syringe: {arm_passive_type.title()} **{arm_name}** Siphon: **{arm_passive_value}** + 10% Health.")
                            elif arm_passive_type == "MANA":
                                reward_list.append(f"🦠 {arm_passive_type.title()} **{arm_name}** Mana: Multiply Enhancer by **{arm_passive_value}**%.")
                            elif arm_passive_type == "ULTIMAX":
                                reward_list.append(f"〽️ {arm_passive_type.title()} **{arm_name}** Ultimax: Increase all move AP by **{arm_passive_value}**.")
                            else:
                                reward_list.append(f"{element_emoji} {arm_passive_type.title()} **{arm_name}** Attack: **{arm_passive_value}** Damage.")
                        else:
                            card = db.queryCard({"NAME": reward})
                            moveset = card['MOVESET']
                            move3 = moveset[2]
                            move2 = moveset[1]
                            move1 = moveset[0]
                            basic_attack_emoji = crown_utilities.set_emoji(list(move1.values())[2])
                            super_attack_emoji = crown_utilities.set_emoji(list(move2.values())[2])
                            ultimate_attack_emoji = crown_utilities.set_emoji(list(move3.values())[2])
                            reward_list.append(f":mahjong: {card['TIER']} **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n:heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}")
        
                    reward_message = "\n\n".join(reward_list)
                    embedVar = discord.Embed(title= f"{title}", description=textwrap.dedent(f"""
                    📽️ **{universe} Scenario Battle!**
                    🔱 **Enemy Level:** {enemy_level}
                    :coin: **Reward** {'{:,}'.format(scenario_gold)}

                    ⚙️ **Difficulty:** {self.difficulty.title()}

                    :crossed_swords: {str(number_of_fights)}
                    """), 
                    colour=0x7289da)
                    embedVar.add_field(name="__**Potential Rewards**__", value=f"{reward_message}")
                    embedVar.set_image(url=scenario_image)
                    # embedVar.set_footer(text=f"")
                    embed_list.append(embedVar)

            return embed_list
        except:
            print("Error setting scenario selection config")


    def set_scenario_config(self, scenario_data):
        try:
            self._list_of_opponents = scenario_data['ENEMIES']
            self._total_enemies = len(self._list_of_opponents)
            self._ai_opponent_card_lvl = int(scenario_data['ENEMY_LEVEL'])
            self._selected_universe = scenario_data['UNIVERSE']
            self._is_available = scenario_data['AVAILABLE']
            self.scenario_easy_drops = scenario_data['EASY_DROPS']
            self.scenario_normal_drops = scenario_data['NORMAL_DROPS']
            self.scenario_hard_drops = scenario_data['HARD_DROPS']

            self.starting_match_title = f"🎞️ Scenario Battle Confirm Start!  ({self._currentopponent + 1}/{self._total_enemies})"
        except:
            print("unable to set scenario config")


    def set_tutorial(self, opponent_did):
        bot_dids = ['837538366509154407', '845672426113466395']

        if opponent_did in bot_dids:
            self._is_tutorial = True
            self.is_ai_opponent = True
            self._is_turn = 0


    def set_starting_turn(self, player_speed, opponent_speed):
        if player_speed >= opponent_speed:
            self._is_turn = 0
        
        if opponent_speed >= player_speed:
            self._is_turn = 1


    def set_explore_config(self, universe_data, card_data):
        try:
            self._selected_universe_data = universe_data
            self.explore_card = card_data
            self._selected_universe = universe_data['TITLE']
        except:
            print("Set explore config did not work")


    def set_corruption_config(self):
        if self._selected_universe_data['CORRUPTED']:
            self._is_corrupted = True
            self.ap_buff = 30
            self.stat_buff = 50
            self.health_buff = 300
            if self.difficulty == "HARD":
                self.ap_buff = 60
                self.stat_buff = 100
                self.health_buff = 1300


    def set_boss_descriptions(self, name_of_boss):
        if self._is_boss:
            boss = db.queryBoss({'NAME': name_of_boss})

            self._arena_boss_description = boss['DESCRIPTION'][0]
            self._arenades_boss_description = boss['DESCRIPTION'][1]
            self._entrance_boss_description = boss['DESCRIPTION'][2]
            self._description_boss_description = boss['DESCRIPTION'][3]
            self._welcome_boss_description = boss['DESCRIPTION'][4]
            self._feeling_boss_description = boss['DESCRIPTION'][5]
            self._powerup_boss_description = boss['DESCRIPTION'][6]
            self._aura_boss_description = boss['DESCRIPTION'][7]
            self._assault_boss_description = boss['DESCRIPTION'][8]
            self._world_boss_description = boss['DESCRIPTION'][9]
            self._punish_boss_description = boss['DESCRIPTION'][10]
            self._rmessage_boss_description = boss['DESCRIPTION'][11]
            self._rebuke_boss_description = boss['DESCRIPTION'][12]
            self._concede_boss_description = boss['DESCRIPTION'][13]
            self._wins_boss_description = boss['DESCRIPTION'][14]
            # boss_special_move_default_msg = t_special_move_description


    def set_who_starts_match(self, player1_speed, player2_speed):
        if player1_speed >= player2_speed:
            self._is_turn = 0
        if player2_speed > player1_speed:
            self._is_turn = 1


    def get_lineup(self):
        self._match_lineup = f"{str(self._currentopponent + 1)}/{str(self._total_enemies)}"


    def get_can_save_match(self):
        if self.mode not in crown_utilities.NOT_SAVE_MODES and self.difficulty != "EASY":
            self._can_save_match = True
        return self._can_save_match


    def get_ai_battle_ready(self):
        # print(self._list_of_opponents)
        self._ai_opponent_card_data = db.queryCard({'NAME': self._list_of_opponents[self._currentopponent]})
        universe_data = db.queryUniverse({'TITLE': {"$regex": str(self._ai_opponent_card_data['UNIVERSE']), "$options": "i"}})
        if self.mode in crown_utilities.DUNGEON_M or self._ai_opponent_card_lvl >= 350:
            title = 'DTITLE'
            arm = 'DARM'
            summon = 'DPET'
        if self.mode in crown_utilities.TALE_M or self._ai_opponent_card_lvl < 350:
            title = 'UTITLE'
            arm = 'UARM'
            summon = 'UPET'

        self._ai_opponent_title_data = db.queryTitle({'TITLE': universe_data[title]})
        self._ai_opponent_arm_data = db.queryArm({'ARM': universe_data[arm]})
        self._ai_opponent_summon_data = db.queryPet({'PET': universe_data[summon]})
        self._ai_opponent_summon_image = self._ai_opponent_summon_data['PATH']
        self._ai_opponent_summon_name = self._ai_opponent_summon_data['PET']
        self._ai_opponent_summon_universe = self._ai_opponent_summon_data['UNIVERSE']

        summon_passive = self._ai_opponent_summon_data['ABILITIES'][0]
        self._ai_opponent_summon_power = list(summon_passive.values())[0]
        self._ai_opponent_summon_ability_name = list(summon_passive.keys())[0]
        self._ai_opponent_summon_type = summon_passive['TYPE']


    def match_has_ended(self, player_1_card, player_2_card, player_3_card=None):
        if player_1_card.health == 0:
            self.match_has_ended = True
            self.player_2_wins = True
        
        if player_2_card.health == 0:
            self.match_has_ended = True
            self.player_1_wins = True

        if player_3_card.health:
            if player_3_card.health == 0:
                self.match_has_ended = True
                self.player_2_wins = True

        if self._is_auto_battle:
            if self._turn_total >= 250:
                self.previous_moves.append(f"⚙️**{player_1_card.name}** could not defeat {player_2_card.name} before the turn Limit...")
                player_1_card.health = 0

        return self.match_has_ended


    def get_previous_moves_embed(self):
        return "\n\n".join(self.previous_moves)
    
    def get_battle_window_title_text(self, opponent_card, your_card, partner_card=None):
        return f"{opponent_card.name}: ❤️{round(opponent_card.health)} 🌀{round(opponent_card.stamina)} 🗡️{round(opponent_card.attack)}/🛡️{round(opponent_card.defense)} {opponent_card._arm_message}\n{your_card.name}: ❤️{round(your_card.health)} 🌀{round(your_card.stamina)} 🗡️{round(your_card.attack)}/🛡️{round(your_card.defense)} {your_card._arm_message}"


    def ai_battle_command(self, your_card, opponent_card):
        aiMove = 0
        
        if your_card.used_resolve and not your_card.summon_used and your_card.stamina >= 30:
            aiMove = 6
        elif opponent_card.move4enh == "WAVE" and (self._turn_total % 10 == 0 or self._turn_total == 0 or self._turn_total == 1):
            if opponent_card.stamina >=20:
                aiMove =4
        elif your_card._barrier_active: #Ai Barrier Checks
            if your_card.stamina >=20: #Stamina Check For Enhancer
                aiMove = ai_enhancer_moves(your_card, opponent_card)
            else:
                aiMove = 1
        elif opponent_card.health <=350: #Killing Blow
            if your_card.move4enh == "BLAST":
                if your_card.stamina >=20:
                    aiMove =4
                else:
                    aiMove =1
            elif your_card.move4enh == "WAVE" and (self._turn_total % 10 == 0 or self._turn_total == 0 or self._turn_total == 1):
                if your_card.stamina >=20:
                    aiMove =4
                else:
                    aiMove =1
            else:
                if your_card.stamina >= 90:
                    aiMove = 1
                elif your_card.stamina >= 80:
                    aiMove =3
                elif your_card.stamina >=30:
                    aiMove=2
                else:
                    aiMove=1
        elif opponent_card.stamina < 10:
            if your_card.move4enh in crown_utilities.Gamble_Enhancer_Check:
                if your_card.stamina >= 20:
                    aiMove = 4
                else:
                    aiMove = 1
            else:
                aiMove = 1
        elif your_card.health <= (.50 * your_card.max_health) and your_card.used_resolve == False and your_card.used_focus:
            aiMove = 5
        elif your_card.stamina >= 160 and (your_card.health >= opponent_card.health):
            aiMove = 3
        elif your_card.stamina >= 160:
            aiMove = 3
        elif your_card.stamina >= 150 and (your_card.health >= opponent_card.health):
            aiMove = 1
        elif your_card.stamina >= 150:
            aiMove = 1
        elif your_card.stamina >= 140 and (your_card.health >= opponent_card.health):
            aiMove = 1
        elif your_card.stamina >= 140:
            aiMove = 3
        elif your_card.stamina >= 130 and (your_card.health >= opponent_card.health):
            aiMove = 1
        elif your_card.stamina >= 130:
            aiMove = 3
        elif your_card.stamina >= 120 and (your_card.health >= opponent_card.health):
            aiMove = 2
        elif your_card.stamina >= 120:
            aiMove = 3
        elif your_card.stamina >= 110 and (your_card.health >= opponent_card.health):
            aiMove = 1
        elif your_card.stamina >= 110:
            aiMove = 2
        elif your_card.stamina >= 100 and (your_card.health >= opponent_card.health):
            if your_card.move4enh in crown_utilities.Gamble_Enhancer_Check or your_card.move4enh in Healer_Enhancer_Check:
                aiMove = 3
            elif your_card.move4enh in crown_utilities.Support_Enhancer_Check or your_card.move4enh in crown_utilities.Stamina_Enhancer_Check or your_card.move4enh in crown_utilities.Turn_Enhancer_Check:
                aiMove = 4
            else:
                aiMove = 1
        elif your_card.stamina >= 100:
            aiMove = 1
        elif your_card.stamina >= 90 and (your_card.health >= opponent_card.health):
            aiMove = 3
        elif your_card.stamina >= 90:
            if your_card.move4enh in crown_utilities.Gamble_Enhancer_Check:
                aiMove = 3
            elif your_card.move4enh in crown_utilities.crown_utilities.Support_Enhancer_Check or your_card.move4enh in crown_utilities.Stamina_Enhancer_Check or your_card.move4enh in crown_utilities.Sacrifice_Enhancer_Check:
                aiMove = 4
            else:
                aiMove = 1
        elif your_card.stamina >= 80 and (your_card.health >= opponent_card.health):
            aiMove = 1
        elif your_card.stamina >= 80:
            aiMove = 3
        elif your_card.stamina >= 70 and (your_card.health >= opponent_card.health):
            if your_card.move4enh in crown_utilities.Gamble_Enhancer_Check:
                aiMove = 1
            else:
                aiMove = ai_enhancer_moves(your_card, opponent_card)
        elif your_card.stamina >= 70:
            aiMove = 1
        elif your_card.stamina >= 60 and (your_card.health >= opponent_card.health):
            if your_card.used_resolve == False and your_card.used_focus:
                aiMove = 5
            elif your_card.used_focus == False:
                aiMove = 2
            else:
                aiMove = 1
        elif your_card.stamina >= 60:
            if your_card.used_resolve == False and your_card.used_focus:
                aiMove = 5
            elif your_card.used_focus == False:
                aiMove = 2
            else:
                aiMove = 1
        elif your_card.stamina >= 50 and (your_card.health >= opponent_card.health):
            if your_card.used_resolve == False and your_card.used_focus:
                aiMove = 5
            elif your_card.used_focus == False:
                aiMove = 2
            else:
                aiMove = 1
        elif your_card.stamina >= 50:
            if your_card.used_resolve == False and your_card.used_focus:
                aiMove = 5
            elif your_card.used_focus == False:
                aiMove = 2
            elif your_card.move4enh in crown_utilities.Support_Enhancer_Check or your_card.move4enh in crown_utilities.Stamina_Enhancer_Check:
                aiMove = 4
            else:
                aiMove = 1
        elif your_card.stamina >= 40 and (your_card.health >= opponent_card.health):
            aiMove = 1
        elif your_card.stamina >= 40:
            aiMove = 2
        elif your_card.stamina >= 30 and (your_card.health >= opponent_card.health):
            if your_card.move4enh in crown_utilities.Gamble_Enhancer_Check:
                aiMove = 1
            elif your_card.move4enh in crown_utilities.Support_Enhancer_Check or your_card.move4enh in crown_utilities.Stamina_Enhancer_Check:
                aiMove = 2
            else:
                aiMove = ai_enhancer_moves(your_card, opponent_card)
        elif your_card.stamina >= 30:
            aiMove = 2
        elif your_card.stamina >= 20 and (your_card.health >= opponent_card.health):
            aiMove = 1
        elif your_card.stamina >= 20:
            if your_card.move4enh in Gamble_Enhancer_Check:
                aiMove = 1
            elif your_card.move4enh in crown_utilities.Support_Enhancer_Check or your_card.move4enh in crown_utilities.Stamina_Enhancer_Check:
                aiMove = 1
            else:
                aiMove = 4
        elif your_card.stamina >= 10:
            aiMove = 1
        else:
            aiMove = 0

        return aiMove


def ai_enhancer_moves(your_card, opponent_card):
    aiMove = 1

    if your_card.move4enh in crown_utilities.Time_Enhancer_Check:
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
    if opponent_card.health <= 200:
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




