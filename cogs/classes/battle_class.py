import db
import crown_utilities

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

        self._is_auto_battle = False

        self._list_of_opponents = []
        self._length_of_opponents = 0
        self._currentopponent = 0
        self._is_turn = 0

        self._selected_universe = ""
        self._selected_universe_data = ""
        self._currentopponent = ""

        self._is_co_op = False
        self._is_duo = False
        self.is_ai_opponent = False
        self._ai_title = ""
        self._ai_arm = ""
        self._ai_summon = ""
        self._ai_level = ""
        
        self.difficulty = self.player.difficulty
        self._is_easy = False
        self._is_hard = False
        self._is_normal = False

        self.health_buff = 0
        self.health_debuff = 0
        self.stat_buff = 0
        self.stat_debuff = 0
        self.ap_buff = 0
        self.ap_debuff = 0

        self.summon_lvl = 0
        self.summon_bond = 0
        self._ai_opponent_card_lvl = 0
        self._ai_can_use_summon = False

        self.scaling_stat = 0
        self._boss_fought_already = False

        self._completed_tales = self.player.completed_tales
        self._completed_dungeons = self.player.completed_dungeons
        self._player_association = ""
        self._name_of_boss = ""

        # Messages
        self.abyss_message = ""

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

        if mode not in crown_utilities.PVP_M:
            self._is_tales = True

        if mode in crown_utilities.AUTO_BATTLE_M:
            self._is_auto_battle = True

        if mode in crown_utilities.AI_CO_OP_M:
            self._is_duo = True
        
        if mode in crown_utilities.CO_OP_M:
            self._is_co_op = True

        if mode in crown_utilities.RAID_M:
            self._is_raid = True

        if mode in crown_utilities.TALE_M:
            self._is_tales = True
            self.summon_lvl = 5
            self.summon_bond = 1
            self._ai_opponent_card_lvl = 30

        
        if mode in crown_utilities.DUNGEON_M:
            self._is_dungeon = True
            self.summon_lvl = 10
            self.summon_bond = 3
            self._ai_opponent_card_lvl = 400
            self.health_buff = self.health_buff + 2000
            self.stat_buff = self.stat_buff + 100
            self.ap_buff = self.ap_buff + 80


        if mode in crown_utilities.BOSS_M:
            self._is_boss = True
            self.summon_lvl = 15
            self.summon_bond = 4
            self._ai_opponent_card_lvl = 1000
            self.health_buff = self.health_buff + 5000
            self.stat_buff = self.stat_buff + 250
            self.ap_buff = self.ap_buff + 250


        if mode == crown_utilities.ABYSS:
            self._is_abyss = True

        if mode == crown_utilities.SCENARIO:
            self._is_scenario = True

        if mode == crown_utilities.EXPLORE:
            self._is_explore = True

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
    


        
    def set_universe_selection_config(self, universe_selection, mode):
        if universe_selection:
            self.selected_universe = universe_selection['SELECTED_UNIVERSE']
            self._selected_universe_data = universe_selection['UNIVERSE_DATA']
            self.crestlist = universe_selection['CREST_LIST']
            self.crestsearch = universe_selection['CREST_SEARCH']
            self._currentopponent =  universe_selection['CURRENTOPPONENT']

            if mode in crown_utilities.BOSS_M:
                self._name_of_boss = universe_selection['BOSS_NAME']
                self._player_association = universe_selection['OGUILD']
                if self.player.boss_fought:
                    self._boss_fought_already = True

            
            if self.crestsearch:
                self._player_association = universe_selection['OGUILD']
            else:
                self._player_association = "PCG"


    def set_abyss_config(self):
        if self._is_abyss:
            try:
                if self._is_easy:
                    self.abyss_message = "The Abyss is unavailable on Easy Mode! Use /difficulty to change your difficulty setting."
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
                self._length_of_opponents = len(self._list_of_opponents)
                self._ai_level = int(abyss['SPECIAL_BUFF'])
                self.abyss_floor = abyss['FLOOR']
                self.abyss_card_to_earn = enemies[-1] 
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
            scenarios = db.queryAllScenariosByUniverse(universe)

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
            self._length_of_opponents = len(self._list_of_opponents)
            self._ai_level = int(scenario_data['ENEMY_LEVEL'])
            self._selected_universe = scenario_data['UNIVERSE']
            self._is_available = scenario_data['AVAILABLE']
            self.scenario_easy_drops = scenario_data['EASY_DROPS']
            self.scenario_normal_drops = scenario_data['NORMAL_DROPS']
            self.scenario_hard_drops = scenario_data['HARD_DROPS']
        except:
            print("unable to set scenario config")


    def set_tutorial(self, opponent_did):
        bot_dids = ['837538366509154407', '845672426113466395']

        if opponent_did in bot_dids:
            self._is_tutorial = True


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

