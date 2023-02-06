import unique_traits as ut
import crown_utilities
import discord
import requests
import textwrap
import db
import random
from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji
from io import BytesIO






class Card:
    try:
        def __init__(self, name, path, price, exclusive, available, is_skin, skin_for, max_health, health, max_stamina, stamina, moveset, attack, defense, type, passive, speed, universe, has_collection, tier, collection, weaknesses, resistances, repels, absorbs, immunity, gif, fpath, rname, rpath):
            self.name = name
            self.fpath= fpath
            self.rpath = rpath
            self.rname = rname
            self.gif = gif
            self.path = path
            self.price = price
            self.exclusive = exclusive
            self.available = available
            self.is_skin = is_skin
            self.skin_for = skin_for
            self.max_health = max_health
            self.health = health
            self.max_stamina = max_stamina
            self.stamina = stamina
            self.moveset = moveset
            self.attack = attack
            self.defense = defense
            self.type = type
            self.passive = passive
            self.speed = speed
            self.universe = universe
            self.has_collection = has_collection
            self.tier = tier
            self.collection = collection
            self.weaknesses = weaknesses
            self.resistances = resistances
            self.repels = repels
            self.absorbs = absorbs
            self.immunity = immunity

            # Universe Traits
            self._final_stand = False
            self._chainsawman_activated = False
            self._atk_chainsawman_buff = False
            self._def_chainsawman_buff = False
            self._demon_slayer_buff = 0
            self._naruto_heal_buff = 0
            self._gow_resolve = False
            self.temp_opp_arm_shield_active = False
            self.temp_opp_shield_value = 0
            self.temp_opp_arm_barrier_active = False
            self.temp_opp_barrier_value = 0
            self.temp_opp_arm_parry_active = False
            self.temp_opp_parry_value = 0
            self.solo_leveling_trait_swapped = False
            self.solo_leveling_trait_active = False

            # Elemental Effect Meters
            self.burn_dmg = 0
            self.poison_dmg = 0
            self.freeze_enh = False
            self.ice_counter = 0
            self.water_buff = 0
            self.shock_buff = 0
            self.psychic_debuff = 0
            self.bleed_damage_counter = 0
            self.bleed_hit = False
            self.basic_water_buff = 0
            self.special_water_buff = 0
            self.ultimate_water_buff = 0
            self.gravity_hit = False
            self.physical_meter = 0

            # Card Defense From Arm
            # Arm Help
            self._shield_active = False
            self._barrier_active = False
            self._parry_active = False
            self._siphon_active = False

            self._shield_value = 0
            self._barrier_value = 0
            self._parry_value = 0
            self._siphon_value = 0
            self._arm_message = ""

            # Card level & level buffs
            self.card_lvl = 0
            self.card_tier = 0
            self.card_exp = 0
            self.card_lvl_attack_buff = 0
            self.card_lvl_defense_buff = 0
            self.card_lvl_hlt_buff = 0
            self.card_lvl_ap_buff = 0
            self.arbitrary_ap_buff = 0

            # Battle requirements
            self.resolved = False
            self.focused = False
            self.dungeon = False
            self.dungeon_card_details = ""
            self.tales_card_details = ""
            self.destiny_card_details = ""
            self.used_focus = False
            self.used_resolve = False
            self.enhancer_used = False
            self.used_summon = False
            self.used_block = False
            self.used_defend = False
            self.focus_count = 0
            self.enhance_turn_iterators = 0
            self.stamina_required_to_focus = 10
            self.stamina_focus_recovery_amount = 90
            self._tutorial_message = ""
            self.resolve_value = 60
            self.summon_resolve_message = ""

            # Talisman Info
            self._talisman = ""

            # Summon Info
            self._summon_ability_name = ""
            self._summon_power = 0
            self._summon_lvl = 0
            self._summon_type = ""
            self._summon_bond = ""
            self._summon_name = ""
            self._summon_image = ""
            self._summon_universe = ""
            self._summon_bondexp = 0
            self._summon_exp = 0

            # Passive Ability
            self.passive_name  = list(passive.keys())[0]
            self.passive_num = list(passive.values())[0]
            self.passive_type = list(passive.values())[1]

            # Each move
            self.m1 = moveset[0]
            self.m2 = moveset[1]
            self.m3 = moveset[2]
            self.enhancer = moveset[3]

            # Move 1
            self.move1 = list(self.m1.keys())[0]
            self.move1ap = list(self.m1.values())[0] + self.card_lvl_ap_buff + self.shock_buff + self.basic_water_buff + self.arbitrary_ap_buff
            self.move1_stamina = list(self.m1.values())[1]
            self.move1_element = list(self.m1.values())[2]
            self.move1_emoji = crown_utilities.set_emoji(self.move1_element)

            # Move 2
            self.move2 = list(self.m2.keys())[0]
            self.move2ap = list(self.m2.values())[0] + self.card_lvl_ap_buff + self.shock_buff + self.special_water_buff + self.arbitrary_ap_buff
            self.move2_stamina = list(self.m2.values())[1]
            self.move2_element = list(self.m2.values())[2]
            self.move2_emoji = crown_utilities.set_emoji(self.move2_element)

            # Move 3
            self.move3 = list(self.m3.keys())[0]
            self.move3ap = list(self.m3.values())[0] + self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff
            self.move3_stamina = list(self.m3.values())[1]
            self.move3_element = list(self.m3.values())[2]
            self.move3_emoji = crown_utilities.set_emoji(self.move3_element)

            # Move Enhancer
            self.move4 = list(self.enhancer.keys())[0]
            self.move4ap = list(self.enhancer.values())[0]
            self.move4_stamina = list(self.enhancer.values())[1]
            self.move4enh = list(self.enhancer.values())[2]

            self.dungeon_card_details
            
            self.pokemon_universe = False

            # Explore Config
            self.bounty = 0
            self.approach_message = " "
            self.bounty_message = " "
            self.battle_message = " "
            self._explore_cardtitle = " "

            # Boss Descriptions
            self._boss_arena_message = ""
            self._boss_arenades_message = ""
            self._boss_entrance_message = ""
            self._boss_description_message = ""
            self._boss_welcome_message = ""
            self._boss_feeling_message = ""
            self._boss_powerup_message = ""
            self._boss_aura_message = ""
            self._boss_assault_message = ""
            self._boss_world_message = ""
            self._boss_punish_message = ""
            self._boss_rmessage_message = ""
            self._boss_rebuke_message = ""
            self._boss_concede_message = ""
            self._boss_wins_message = ""
            self._special_description = ""

            self.affinity_message = ""
            self.price_message = ""
            self.card_icon = ""
            self.trait_message = ""
            self.universe_buff_message = " "

            self.universe_image = ""
            self.tip = ""
            self.view_card_message = ""
            self.universe_crest = crown_utilities.crest_dict[self.universe]
            self.index = ""

            if self.passive_type:
                value_for_passive = self.tier * .5
                flat_for_passive = round(10 * (self.tier * .5))
                stam_for_passive = 5 * (self.tier * .5)
                if self.passive_type == "HLT":
                    self.passive_num = value_for_passive
                if self.passive_type == "LIFE":
                    self.passive_num = value_for_passive
                if self.passive_type == "ATK":
                    self.passive_num = flat_for_passive
                if self.passive_type == "DEF":
                    self.passive_num = flat_for_passive
                if self.passive_type == "STAM":
                    self.passive_num = stam_for_passive
                if self.passive_type == "DRAIN":
                    self.passive_num = stam_for_passive
                if self.passive_type == "FLOG":
                    self.passive_num = value_for_passive
                if self.passive_type == "WITHER":
                    self.passive_num = value_for_passive
                if self.passive_type == "RAGE":
                    self.passive_num = value_for_passive
                if self.passive_type == "BRACE":
                    self.passive_num = value_for_passive
                if self.passive_type == "BZRK":
                    self.passive_num = value_for_passive
                if self.passive_type == "CRYSTAL":
                    self.passive_num = value_for_passive
                if self.passive_type == "FEAR":
                    self.passive_num = flat_for_passive
                if self.passive_type == "GROWTH":
                    self.passive_num = flat_for_passive
                if self.passive_type == "CREATION":
                    self.passive_num = value_for_passive
                if self.passive_type == "DESTRUCTION":
                    self.passive_num = value_for_passive
                if self.passive_type == "SLOW":
                    self.passive_num = "1"
                if self.passive_type == "HASTE":
                    self.passive_num = "1"
                if self.passive_type == "STANCE":
                    self.passive_num = flat_for_passive
                if self.passive_type == "CONFUSE":
                    self.passive_num = flat_for_passive
                if self.passive_type == "BLINK":
                    self.passive_num = stam_for_passive

    except:
        print("ERRRO")

    def is_universe_unbound(self):
        if(self.universe == "Unbound"):
            return True

    # AI ONLY BUFFS
    def set_ai_card_buffs(self, _ai_lvl_buff, _ai_stat_buff, _ai_stat_debuff, _ai_health_buff, _ai_health_debuff, _ai_ap_buff, _ai_ap_debuff):
        self.card_lvl = _ai_lvl_buff

        self.card_lvl_ap_buff = crown_utilities.level_sync_stats(self.card_lvl, "AP")
        self.card_lvl_attack_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_defense_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_hlt_buff = crown_utilities.level_sync_stats(self.card_lvl, "HLT")

        self.max_health = self.max_health + self.card_lvl_hlt_buff + _ai_health_buff + _ai_health_debuff
        self.health = self.health + self.card_lvl_hlt_buff + _ai_health_buff + _ai_health_debuff
        self.attack = self.attack + self.card_lvl_attack_buff + _ai_stat_buff + _ai_stat_debuff
        self.defense = self.defense + self.card_lvl_defense_buff + _ai_stat_buff + _ai_stat_debuff
        self.move1ap = self.move1ap + self.card_lvl_ap_buff + _ai_ap_buff + _ai_ap_debuff
        self.move2ap = self.move2ap + self.card_lvl_ap_buff + _ai_ap_buff + _ai_ap_debuff
        self.move3ap = self.move3ap + self.card_lvl_ap_buff + _ai_ap_buff + _ai_ap_debuff


    # This method will set the level buffs & apply them
    def set_card_level_buffs(self, list_of_card_levels=None):
        try:
            if list_of_card_levels:
                for x in list_of_card_levels:
                    if x['CARD'] == self.name:
                        self.card_lvl = x['LVL']
                        self.card_exp = x['EXP']
                        self.card_lvl_ap_buff = crown_utilities.level_sync_stats(self.card_lvl, "AP")
                        self.card_lvl_attack_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
                        self.card_lvl_defense_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
                        self.card_lvl_hlt_buff = crown_utilities.level_sync_stats(self.card_lvl, "HLT")
                
            # If not leveling from card lvl vault
            if not list_of_card_levels:
                self.card_lvl_ap_buff = crown_utilities.level_sync_stats(self.card_lvl, "AP")
                self.card_lvl_attack_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
                self.card_lvl_defense_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
                self.card_lvl_hlt_buff = crown_utilities.level_sync_stats(self.card_lvl, "HLT")

            # applying buffs. If no buffs, adds 0
            self.max_health = self.max_health + self.card_lvl_hlt_buff
            self.health = self.health + self.card_lvl_hlt_buff
            self.attack = self.attack + self.card_lvl_attack_buff
            self.defense = self.defense + self.card_lvl_defense_buff
            self.move1ap = self.move1ap + self.card_lvl_ap_buff
            self.move2ap = self.move2ap + self.card_lvl_ap_buff
            self.move3ap = self.move3ap + self.card_lvl_ap_buff


        except:
            print("Error setting card levels")
            return False


    async def set_guild_stat_level_buffs(self, guild_name):
        try:
            guild_buff = await crown_utilities.guild_buff_update_function(guild_name.lower())
            
            if guild_buff:
                if guild_buff['Stat']:
                    self.card_lvl_ap_buff = 100
                    self.card_lvl_attack_buff = 100
                    self.card_lvl_defense_buff = 100
                    self.card_lvl_hlt_buff = 300

                    self.max_health = self.max_health + self.card_lvl_hlt_buff
                    self.health = self.health + self.card_lvl_hlt_buff
                    self.attack = self.attack + self.card_lvl_attack_buff
                    self.defense = self.defense + self.card_lvl_defense_buff
                    self.move1ap = self.move1ap + self.card_lvl_ap_buff
                    self.move2ap = self.move2ap + self.card_lvl_ap_buff
                    self.move3ap = self.move3ap + self.card_lvl_ap_buff
                    update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])

        except:
            print("Error setting guild level stats")
            return False


    def set_trait_message(self):
            for trait in ut.traits:
                if trait['NAME'] == self.universe:
                    mytrait = trait
                if self.universe == 'Kanto Region' or self.universe == 'Johto Region' or self.universe == 'Kalos Region' or self.universe == 'Unova Region' or self.universe == 'Sinnoh Region' or self.universe == 'Hoenn Region' or self.universe == 'Galar Region' or self.universe == 'Alola Region':
                    self.pokemon_universe = True
                    if trait['NAME'] == 'Pokemon':
                        mytrait = trait
            if mytrait:
                self.traitmessage = f"{mytrait['EFFECT']}: {mytrait['TRAIT']}"
            else:
                self.traitmessage = ""

            return self.traitmessage    


    def set_price_message_and_card_icon(self):
        if self.is_skin:
            self.price_message = "Card Skin"
            self.card_icon = f"💎"
        elif self.exclusive or self.has_collection:
            if self.has_collection == True:
                self.price_message = "Destiny Only"
                self.card_icon = f"✨"
            else:
                self.price_message = "Dungeon Only"
                self.card_icon = f"🔥"
                self.dungeon = True
        elif self.exclusive == False and self.available == False and self.has_collection == False:
            self.price_message = "Boss Only"
            self.card_icon = f"👹"
        else:
            self.price_message = f"Shop & Drop"
            self.card_icon = f"🎴"


    def set_affinity_message(self):
        try:
            weakness_list = []
            resistance_list = []
            repels_list = []
            absorb_list = []
            immune_list = []

            message_list = []

            weakness_msg = ""
            resistances_msg = ""
            repels_msg = ""
            absorb_msg = ""
            immune_msg = ""

            message_to = ""

            for weakness in self.weaknesses:
                if weakness:
                    emoji = crown_utilities.set_emoji(weakness)
                    weakness_list.append(emoji)

            for resistance in self.resistances:
                if resistance:
                    emoji = crown_utilities.set_emoji(resistance)
                    resistance_list.append(emoji)

            for repel in self.repels:
                if repel:
                    emoji = crown_utilities.set_emoji(repel)
                    repels_list.append(emoji)

            for absorb in self.absorbs:
                if absorb:
                    emoji = crown_utilities.set_emoji(absorb)
                    absorb_list.append(emoji)

            for immune in self.immunity:
                if immune:
                    emoji = crown_utilities.set_emoji(immune)
                    immune_list.append(emoji)

            if weakness_list:
                weakness_msg = " ".join(weakness_list)
                message_list.append(f"**Weaknesses:** {weakness_msg}")
            
            if resistance_list:
                resistances_msg = " ".join(resistance_list)
                message_list.append(f"**Resistances:** {resistances_msg}")
            
            if repels_list:
                repels_msg = " ".join(repels_list)
                message_list.append(f"**Repels:** {repels_msg}")

            if absorb_list:
                absorb_msg = " ".join(absorb_list)
                message_list.append(f"**Absorbs:** {absorb_msg}")

            if immune_list:
                immune_msg = " ".join(immune_list)
                message_list.append(f"**Immunity:** {immune_msg}")

            if message_list:
                message_to = "\n".join(message_list)
            
            if  not message_list:
                message_to = "No Affinities"

            self.affinity_message = textwrap.dedent(f"""\
            {message_to}
            """)

            return self.affinity_message

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


    def set_universe_image(self):
        self.universe_image = db.queryUniverse({'TITLE': self.universe})['PATH']
        return self.universe_image
    

    def set_tip_and_view_card_message(self):
        if self.is_skin:
            self.view_card_message = f"{self.name} is a card Skin. "
            self.tip = f"Earn the {self.skin_for} card and use gems to /craft this Skin!"
        elif self.has_collection == True or self.dungeon == True:
            if self.has_collection:
                self.view_card_message = f"{self.name} is a Destiny card. "
                self.tip = f"Complete {self.universe} Destiny: {self.collection} to unlock this card."
            else:
                self.view_card_message = f"{self.name} is a Dungeon card. "
                self.tip = f"/craft or Find this card in the {self.universe} Dungeon"
        elif self.has_collection == False and self.available == False and self.exclusive == False:
            self.view_card_message = f"{self.name} is a Boss card. "
            self.tip = f"Defeat {self.universe} Boss to earn this card."
        elif self.attack > self.defense:
            self.view_card_message = f"{self.name} is an offensive card. "
            self.tip = f"Tip: Equipping {self.universe} /titles and defensive /arms would help boost survivability"
        elif self.defense > self.attack:
            self.view_card_message = f"{self.name} is a defensive card. "
            self.tip = f"Tip: Equipping {self.universe} /titles and offensive /arms would help boost killability"
        else:
            self.view_card_message = f"{self.name} is a balanced card. "
            self.tip = f"Tip: Equip {self.universe} /titles and /arms that will maximize your Enhancer"

    
    def set_arm_config(self, arm_type, arm_name, arm_value, arm_element=None):
        try:
            if arm_type == "BASIC":
                self.move1 = arm_name
                self.move1ap = arm_value + self.card_lvl_ap_buff
                self.move1_element = arm_element
                self.move1_emoji = crown_utilities.set_emoji(self.move1_emoji)

            if arm_type == "SPECIAL":
                self.move2 = arm_name
                self.move2ap = arm_value + self.card_lvl_ap_buff
                self.move2_element = arm_element
                self.move2_emoji = crown_utilities.set_emoji(self.move2_emoji)

            if arm_type == "ULTIMATE":
                self.move3 = arm_name
                self.move3ap = arm_value + self.card_lvl_ap_buff
                self.move3_element = arm_element
                self.move3_emoji = crown_utilities.set_emoji(self.move3_emoji)

            if arm_type == "ULTIMAX":
                self.move1ap = self.move1ap + arm_value
                self.move2ap = self.move2ap + arm_value
                self.move3ap = self.move3ap + arm_value

            if arm_type == "SHIELD":
                self._shield_active = True
                self._shield_value = self._shield_value + arm_value

            if arm_type == "BARRIER":
                self._barrier_active = True
                self._barrier_value = self._barrier_value + arm_value

            if arm_type == "PARRY":
                self._parry_active = True
                self._parry_value = self._parry_value + arm_value

            if arm_type == "SIPHON":
                self._siphon_active = True
                self._siphon_value = self._siphon_value + arm_value

            if arm_type == "MANA":
                self.move4ap = self.move4ap * (arm_value / 100)

        except:
            print("Error")


    def set_universal_buffs(self, arm_universe, title_universe):
        if (arm_universe == self.universe) and (title_universe == self.universe):
            self.attack = self.attack + 20
            self.defense = self.defense + 20
            self.health = self.health + (150 * self.tier)
            self.max_health = self.max_health  + (150 * self.tier)
            self.universe_buff_message = "__Universe Buff Applied__"
            if self.has_collection:
                self.attack = self.attack + 25
                self.defense = self.defense + 25
                self.health = self.health + (50 * self.tier)
                self.max_health = self.max_health  + (50 * self.tier)
                self.universe_buff_message = "__Destiny Buff Applied__"


    def set_card_level_icon(self):
        if self.card_lvl >= 200:
            licon ="🔱"
        if self.card_lvl >= 700:
            licon ="⚜️"
        if self.card_lvl >=999:
            licon ="🏅"
        
        return licon


    # Explore Methods    
    def set_explore_bounty_and_difficulty(self, battle):
        if self.tier == 1:
            self.bounty = random.randint(5000, 10000)
        if self.tier == 2:
            self.bounty = random.randint(15000, 20000)
        if self.tier == 3:
            self.bounty = random.randint(20000, 24000)
        if self.tier == 4:
            self.bounty = random.randint(25000, 40000)
        if self.tier == 5:
            self.bounty = random.randint(50000, 60000)
        if self.tier == 6:
            self.bounty = random.randint(100000, 150000)
        if self.tier == 7:
            self.bounty = random.randint(200000, 300000)

        mode_selector_randomizer = random.randint(0, 200)

        if mode_selector_randomizer >= 100:
            selected_mode = "Easy"
            self.approach_message = "💡 A Basic "
            self._explore_cardtitle = {'TITLE': 'Universe Title'}
            self.card_lvl = random.randint(5, 30)


        if mode_selector_randomizer <= 99 and mode_selector_randomizer >= 70:
            selected_mode = "Normal"
            self.approach_message = "👑 A Formidable "
            self._explore_cardtitle = {'TITLE': 'Universe Title'}
            self.card_lvl = random.randint(50, 200)
            self.bounty = self.bounty * 5

        if mode_selector_randomizer <= 69 and mode_selector_randomizer >= 20:
            selected_mode = "Hard"
            self.approach_message = "🔥 An Empowered "
            self._explore_cardtitle = {'TITLE': 'Dungeon Title'}
            self.card_lvl = random.randint(350, 600)
            self.bounty = self.bounty * 30


        if mode_selector_randomizer <= 19:
            selected_mode = "Impossible"
            self.approach_message = "😈 An Impossible "
            self._explore_cardtitle = {'TITLE': 'Dungeon Title'}
            self.card_lvl = random.randint(850, 1500)
            self.bounty = self.bounty * 150


        if battle._is_hard:
            self.attack = self.attack + 1250
            self.defense = self.defense + 1250
            self.max_health = self.max_health + 3000
            self.health = self.health + 3000
            self.bounty = self.bounty + 15000000

        if self.bounty >= 150000:
            bounty_icon = ":money_with_wings:"
        elif self.bounty >= 100000:
            bounty_icon = ":moneybag:"
        elif self.bounty >= 50000 or self.bounty <= 49999:
            bounty_icon = ":dollar:"



        self.card_lvl_attack_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_defense_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_ap_buff = crown_utilities.level_sync_stats(self.card_lvl, "AP")
        self.card_lvl_hlt_buff = crown_utilities.level_sync_stats(self.card_lvl, "HLT")



        self.bounty_message = f"{bounty_icon} {'{:,}'.format(self.bounty)}"
        self.battle_message = "Glory: Defeat the card and earn the card and the bounty, but if you lose you lose gold! Gold: Earn gold only!"

        self.set_card_level_buffs(None)


    # Element Methods
    def set_shock_buff(self, num=0):
        self.shock_buff =  self.shock_buff + num


    def set_water_buff(self, num=0):
        if self.move1_element == "WATER":
            self.basic_water_buff = self.basic_water_buff + num
        
        if self.move2_element == "WATER":
            self.special_water_buff = self.special_water_buff + num

        if self.move3_element == "WATER":
            self.ultimate_water_buff = self.ultimate_water_buff + num


    def set_bleed_hit(self, turn_total, opponent_card):
        if opponent_card.bleed_hit:
            opponent_card.bleed_hit = False
            bleed_hit_local = 10 * turn_total
            self.health = self.health - bleed_hit_local
            if self.health < 0:
                self.health = 0
            return f"🩸 **{self.name}** shredded for **{round(bleed_hit_local)}** bleed dmg..."


    def set_burn_hit(self, opponent_card):
        if opponent_card.burn_dmg > 3:
            self.health = self.health - opponent_card.burn_dmg
            return f"🔥 **{self.name}** burned for **{round(opponent_card.burn_dmg)}** dmg..."
            if self.health < 0:
                self.health = 0

        if opponent_card.burn_dmg >= 2:
            opponent_card.burn_dmg = round(opponent_card.burn_dmg / 2)



    def frozen(self, battle, opponent_card):
        if opponent_card.freeze_enh:
            battle.turn_total = battle.turn_total + 1
            _battle.next_turn()

        return {"MESSAGE" : f"❄️ **{self.name}** has been frozen for a turn...", "TURN": _battle._is_turn}


    def set_poison_hit(self, opponent_card):
        if opponent_card.poison_dmg:
            self.health = self.health - opponent_card.poison_dmg
            if self.health <  0:
                self.health = 0
            return f"🧪 **{self.name}** poisoned for **{opponent_card.poison_dmg}** dmg..."


    def set_gravity_hit(self):
        if self.gravity_hit:
            self.gravity_hit = False


    def set_solo_leveling_config(self, opponent_shield_active, opponent_shield_value, opponent_barrier_active, opponent_barrier_value, opponent_parry_active, opponent_parry_value):
        if self.universe == "Solo Leveling":
            self.solo_leveling_trait_active = True 
            self.temp_opp_arm_shield_active = opponent_shield_active
            self.temp_opp_shield_value = opponent_shield_value
            self.temp_opp_arm_barrier_active = opponent_barrier_active
            self.temp_opp_barrier_value = opponent_barrier_value
            self.temp_opp_arm_parry_active = opponent_parry_active
            self.temp_opp_parry_value = opponent_parry_value


    def activate_solo_leveling_trait(self, _battle, opponent_card):
        if self.universe == "Solo Leveling" and not self.solo_leveling_trait_swapped:
            if opponent_card.temp_opp_arm_shield_active and not opponent_card._shield_active:
                if self._shield_active:
                    self._shield_value = self._shield_value + opponent_card._shield_value
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
                elif not self._shield_active:
                    self._shield_active = True
                    self._shield_value = opponent_card.temp_opp_shield_value
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
            
            elif temp_opp_arm_parry_active and not opponent_card._barrier_active:
                if self._barrier_active:
                    self._barrier_value = self._barrier_value + opponent_card.temp_opp_barrier_value
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
                elif not self._barrier_active:
                    self._barrier_active = True
                    self._barrier_value = opponent_card.temp_opp_barrier_value
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
            
            elif opponent_card.temp_opp_arm_parry_active and not opponent_card._parry_value:
                if self._parry_active:
                    self._parry_value = self._parry_value + opponent_card.temp_opp_parry_value
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
                elif not self._parry_active:
                    self._parry_active = True
                    self._parry_value = opponent_card.temp_opp_parry_value
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True


    def set_deathnote_message(self, _battle):
        if _battle._turn_total == 0 and not _battle._turn_zero_has_happened:
            _battle._turn_zero_has_happened = True
            if self.universe == "Death Note":
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Scheduled Death 📓")


    def set_souls_trait(self):
        if self.used_resolve and self.universe == "Souls":
            self.move2 = self.move3
            self.move2ap = self.move3ap
            self.move2_stamina = self.move3_stamina
            self.move2_element = self.move3_element
            self.move2_emoji = self.move3_emoji


    def get_card_index(self, list_of_cards):
        try:
            self.index = list_of_cards.index(self.name)
            return self.index
        except:
            return 0


    def showcard(self, mode, arm, title, turn_total, opponent_card_defense):
    # Card Name can be 16 Characters before going off Card
    # Lower Card Name Font once after 16 characters
        try:    
            if self.health <= 0:
                im = get_card(self.path, self.name, "base")
                im.save("text.png")
                return discord.File("text.png")
            else:
                if self.used_resolve:
                    im = get_card(self.rpath, self.rname, "resolve")
                elif self.used_focus:
                    if self.fpath:
                        im = get_card(self.fpath, self.name, "focus")
                    else:
                        im = get_card(self.path, self.name, "base")
                else:
                    im = get_card(self.path, self.name, "base")

                draw = ImageDraw.Draw(im)

                # Font Size Adjustments
                # Name not go over Card
                name_font_size = 60
                title_font_size = 35
                basic_font_size = 30
                super_font_size = 30
                ultimate_font_size = 30
                enhancer_font_size = 30
                title_size = (600, 65)
                if len(list( self.name)) >= 15 and not self.used_resolve:
                    name_font_size = 45
                if len(list( self.rname)) >= 15 and self.used_resolve:
                    name_font_size = 45
                if len(list( self.name)) >= 18 and not self.used_resolve:
                    name_font_size = 40
                    title_size = (600, 80)
                if len(list( self.rname)) >= 18 and self.used_resolve:
                    name_font_size = 40
                    title_size = (600, 80)
                if len(list( self.name)) >= 25 and not self.used_resolve:
                    name_font_size = 35
                    title_size = (600, 80)
                if len(list( self.rname)) >= 25 and self.used_resolve:
                    name_font_size = 35
                    title_size = (600, 80)

                if type(title) is dict:
                    title_len = int(len(list(title['TITLE'])))
                    title_message = f"{title['TITLE']}"
                else:
                    title_message = f"{title.passive_type.title()} {title.passive_value}"
                    title_len = int(len(list(title.name)))


                card_message = f"{self.passive_type.title()} {self.passive_num}"
                    
                #Moveset Emojis
                    
                engagement_basic = 0
                engagement_special = 0
                engagement_ultimate = 0
                ebasic = '💢'
                especial = '💢'
                eultimate = '🗯️'
                if opponent_card_defense is None:
                    ebasic = ' '
                    especial = ' '
                    eultimate = ' '
                else:
                    defensepower = opponent_card_defense - self.attack
                    if defensepower <=0:
                        defensepower = 1
                    
                    basic_ability_power =  self.attack - opponent_card_defense + self.move1ap
                    if basic_ability_power <= 0:
                        basic_ability_power = self.move1ap
                    
                    basic = round((basic_ability_power / defensepower))
                    if basic > (self.move1ap * 2):
                        engagement_basic = 5
                        ebasic = '❌x2'
                    elif basic > (self.move1ap * 1.5):
                        engagement_basic = 4
                        ebasic = '〽️x1.5'
                    elif basic >= (self.move1ap * 1.1):
                        engagement_basic = 3
                        ebasic = '‼️'
                    elif basic < (self.move1ap / 2)  and basic > (self.move1ap / 3):
                        engagement_basic = 2
                        ebasic = '❕'
                    elif basic < (self.move1ap / 3):
                        engagement_basic = 1
                        ebasic = '💢'
                
                    special_ability_power =  self.attack - opponent_card_defense + self.move2ap
                    if special_ability_power <= 0:
                        special_ability_power = self.move2ap
                        
                    special = round(special_ability_power/ defensepower)
                    if special > (self.move2ap * 2):
                        engagement_special = 5
                        especial = '❌x2'
                    elif special > (self.move2ap * 1.5):
                        engagement_special = 4
                        especial = '〽️x1.5'
                    elif special >= (self.move2ap * 1.1):
                        engagement_special = 3
                        especial = '‼️'
                    elif special < (self.move2ap / 2) and special > (self.move2ap / 3):
                        engagement_special = 2
                        especial = '❕'
                    elif special < (self.move2ap / 3):
                        engagement_special = 1
                        especial = '💢'
            
                    ultimate_ability_power =  self.attack - opponent_card_defense + self.move3ap
                    if ultimate_ability_power <= 0:
                        ultimate_ability_power = self.move3ap
                    ultimate = round(ultimate_ability_power / defensepower)
                    if ultimate > (self.move3ap * 2):
                        engagement_ultimate = 5
                        eultimate = '❌x2'
                    elif ultimate > (self.move3ap * 1.5):
                        engagement_ultimate = 4
                        eultimate = '〽️x1.5'
                    elif ultimate >= (self.move3ap * 1.1):
                        engagement_ultimate = 3
                        eultimate = '‼️'
                    elif ultimate < (self.move3ap / 2) and ultimate > (self.move3ap / 3):
                        engagement_ultimate = 2
                        eultimate = '❕'
                    elif ultimate < (self.move3ap / 3):
                        engagement_ultimate = 1
                        eultimate = '💢'


                if arm != "none":
                    arm_message = f"{arm.passive_type.title()} {arm.passive_value}"
                    if arm.passive_type in crown_utilities.ABILITY_ARMS:
                        arm_message = "Ability Arm"
                    

                if mode == "non-battle":
                    ebasic = ""
                    especial = ""
                    eultimate = ""
                move1_text = f"{self.move1_emoji} {self.move1}: {self.move1ap} {ebasic}"
                move2_text = f"{self.move2_emoji} {self.move2}: {self.move2ap} {especial}"
                move3_text = f"{self.move3_emoji} {self.move3}: {self.move3ap} {eultimate}"
                

                turn_crit = False
                if self.move4enh in crown_utilities.Turn_Enhancer_Check:
                    if turn_total == 0:
                        self.move4ap = round(self.move4ap)
                        turn_crit = True
                    elif turn_total % 10 == 0:
                        self.move4ap = round(self.move4ap)
                        turn_crit = True
                    elif turn_total >= 1:
                        self.move4ap = round(self.move4ap / turn_total)

                elif self.move4enh in crown_utilities.Damage_Enhancer_Check:
                    if turn_total > 0:
                        self.move4ap = round(self.move4ap * turn_total)
                        if self.move4ap >= (100 * self.tier):
                            if self.move4enh == "BLAST":
                                self.move4ap = (100 * self.tier)
                            else:
                                self.move4ap = (100 * self.tier)
                            turn_crit = True
                
                # move4enh is the TYPE of enhancer
                if not turn_crit:
                    move_enhanced_text = f"🦠 {self.move4}: {self.move4enh} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"
                elif self.move4enh in crown_utilities.Damage_Enhancer_Check and self.move4ap == (100 * card_tier):
                    move_enhanced_text = f"🎇 {self.move4}: {self.move4enh} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"
                elif self.move4enh in crown_utilities.Turn_Enhancer_Check and (turn_total % 10 == 0 or turn_total == 0):
                    move_enhanced_text = f"🎇 {self.move4}: {self.move4enh} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"
                else:
                    move_enhanced_text = f"🎇 {self.move4}: {self.move4enh} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"


                #Moveset Length
                
                basic_length = int(len(move1_text))
                super_length = int(len(move2_text))
                ultimate_length = int(len(move3_text))
                enhancer_length = int(len(move_enhanced_text))
                
                
                if basic_length >= 53:
                    basic_font_size = 27
                if basic_length >= 60:
                    basic_font_size = 25
                if basic_length >= 65:
                    basic_font_size = 23
                    
                if super_length >= 53:
                    super_font_size = 27
                if super_length >= 60:
                    super_font_size = 25
                if super_length >= 65:
                    super_font_size = 23
                    
                if ultimate_length >= 53:
                    ultimate_font_size = 27
                if ultimate_length >= 60:
                    ultimate_font_size = 25
                if ultimate_length >= 65:
                    ultimate_font_size = 23
                    
                if enhancer_length >= 53:
                    enhancer_font_size = 27
                if enhancer_length >= 60:
                    enhancer_font_size = 25
                if enhancer_length >= 65:
                    enhancer_font_size = 23
                    
                
                header = ImageFont.truetype("YesevaOne-Regular.ttf", name_font_size)
                title_font = ImageFont.truetype("YesevaOne-Regular.ttf", title_font_size)
                passive_font = ImageFont.truetype("YesevaOne-Regular.ttf", 35)
                s = ImageFont.truetype("Roboto-Bold.ttf", 22)
                h = ImageFont.truetype("YesevaOne-Regular.ttf", 37)
                m = ImageFont.truetype("Roboto-Bold.ttf", 25)
                r = ImageFont.truetype("Freedom-10eM.ttf", 40)
                lvl_font = ImageFont.truetype("Neuton-Bold.ttf", 68)
                health_and_stamina_font = ImageFont.truetype("Neuton-Light.ttf", 41)
                attack_and_shield_font = ImageFont.truetype("Neuton-Bold.ttf", 48)
                moveset_font_1 = ImageFont.truetype("antonio.regular.ttf", basic_font_size)
                moveset_font_2 = ImageFont.truetype("antonio.regular.ttf", super_font_size)
                moveset_font_3 = ImageFont.truetype("antonio.regular.ttf", ultimate_font_size)
                moveset_font_4 = ImageFont.truetype("antonio.regular.ttf", enhancer_font_size)
                rhs = ImageFont.truetype("destructobeambb_bold.ttf", 35)
                stats = ImageFont.truetype("Freedom-10eM.ttf", 30)
                card_details_font_size = ImageFont.truetype("destructobeambb_bold.ttf", 25)
                card_levels = ImageFont.truetype("destructobeambb_bold.ttf", 40)
                

                if self.health == self.max_health:
                    health_bar = f"{round(self.max_health)}"
                else:
                    health_bar = f"{round(self.health)}/{round(self.max_health)}"

                # Character & Title Name
                if not self.resolved:
                    draw.text(title_size,  self.name, (255, 255, 255), font=header, stroke_width=1, stroke_fill=(0, 0, 0),
                            align="left")
                if self.resolved:
                    if  self.rname != "":
                        draw.text(title_size,  self.rname, (255, 255, 255), font=header, stroke_width=1, stroke_fill=(0, 0, 0),
                                align="left")
                    else:
                        draw.text(title_size,  self.name, (255, 255, 255), font=header, stroke_width=1, stroke_fill=(0, 0, 0),
                                align="left")

                # Level
                lvl_sizing = (89, 70)
                if int(self.card_lvl) > 9:
                    lvl_sizing = (75, 70)
                if int(self.card_lvl) > 99:
                    lvl_sizing = (55, 70)
                draw.text(lvl_sizing, f"{self.card_lvl}", (255, 255, 255), font=lvl_font, stroke_width=1, stroke_fill=(0, 0, 0),
                        align="center")

                # Health & Stamina
                rift_universes = ['Crown Rift Awakening']
                if self.universe in rift_universes:
                    draw.text((730, 417), health_bar, (0, 0, 0), font=health_and_stamina_font, align="left")
                    draw.text((730, 457), f"{stamina}", (0, 0, 0), font=health_and_stamina_font, align="left")
                else:
                    draw.text((730, 417), health_bar, (255, 255, 255), font=health_and_stamina_font, stroke_width=1,
                            stroke_fill=(0, 0, 0), align="left")
                    draw.text((730, 457), f"{self.stamina}", (255, 255, 255), font=health_and_stamina_font, stroke_width=1,
                            stroke_fill=(0, 0, 0), align="left")

                # Attack & Shield (Defense)
                a_sizing = (89, 515)
                d_sizing = (1062, 515)
                if int(self.attack) > 99:
                    a_sizing = (78, 515)
                if int(self.defense) > 99:
                    d_sizing = (1048, 515)
                if int(self.attack) > 999:
                    a_sizing = (70, 515)
                if int(self.defense) > 999:
                    d_sizing = (1040, 515)


                draw.text(a_sizing, f"{round(self.attack)}", (255, 255, 255), font=attack_and_shield_font, stroke_width=1,
                        stroke_fill=(0, 0, 0), align="center")
                draw.text(d_sizing, f"{round(self.defense)}", (255, 255, 255), font=attack_and_shield_font, stroke_width=1,
                        stroke_fill=(0, 0, 0), align="center")

                
                
                # attack_stat = f"🗡️{round(attack)}"
                # defense_stat = f"🛡️{round(defense)}"
                if type(title) is dict:
                    title_message_on_card = f"🎗️ None 🦾 None"
                else:
                    title_suffix = crown_utilities.title_enhancer_suffix_mapping[title.passive_type]
                    if mode == "battle":
                        title_message_on_card = f"🎗️ {title_message}{title_suffix}"
                    else:
                        title_message_on_card = f"🎗️ {title_message}{title_suffix}  🦾 {arm_message}"


                card_suffix = crown_utilities.passive_enhancer_suffix_mapping[self.passive_type]

                with Pilmoji(im) as pilmoji:
                    pilmoji.text((602, 138), f"{title_message_on_card}", (255, 255, 255), font=title_font, stroke_width=1, stroke_fill=(0, 0, 0),
                        align="left")
                    pilmoji.text((602, 180), f"🩸 {card_message}{card_suffix} 🏃 {self.speed}", (255, 255, 255), font=passive_font, stroke_width=1, stroke_fill=(0, 0, 0),
                        align="left")
                    pilmoji.text((600, 250), move1_text.strip(), (255, 255, 255), font=moveset_font_1, stroke_width=2,
                                stroke_fill=(0, 0, 0))
                    pilmoji.text((600, 290), move2_text.strip(), (255, 255, 255), font=moveset_font_2, stroke_width=2,
                                stroke_fill=(0, 0, 0))
                    pilmoji.text((600, 330), move3_text.strip(), (255, 255, 255), font=moveset_font_3, stroke_width=2,
                                stroke_fill=(0, 0, 0))
                    pilmoji.text((600, 370), move_enhanced_text.strip(), (255, 255, 255), font=moveset_font_4, stroke_width=2,
                                stroke_fill=(0, 0, 0))

                    # pilmoji.text((40, 545), "🗡️", (255, 255, 255), font=moveset_font, stroke_width=2,
                    #              stroke_fill=(0, 0, 0))
                    # pilmoji.text((1000, 545), "🛡️", (255, 255, 255), font=moveset_font, stroke_width=2,
                    #              stroke_fill=(0, 0, 0))
                # Moveset End

                with BytesIO() as image_binary:
                    im.save(image_binary, "PNG")
                    image_binary.seek(0)
                    # await ctx.send(file=discord.File(fp=image_binary,filename="image.png"))
                    file = discord.File(fp=image_binary,filename="image.png")
                    return file

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


    def damage_cal(self, selected_move, _battle, _opponent_card):
        if _opponent_card.defense <= 0:
            _opponent_card.defense = 25
        if self.attack <= 0:
            self.attack = 25
        if _opponent_card.defense <= 0:
            _opponent_card.defense = 25
        if _opponent_card.attack <= 0:
            _opponent_card.attack = 25

        enhancer = False
        can_use_move_flag = True
        move_element = ""

        ENHANCERS = [4]
        MOVES = [1,2,3]

        if selected_move in MOVES:
            does_repel = False
            does_absorb = False
            is_wind_element = False
            is_physical_element = False
            ranged_attack = False
            wind_buff = 0

            if selected_move == 1:
                move = self.move1
                ap = self.move1ap
                move_stamina = self.move1_stamina
                can_use_move_flag = True
                move_element = self.move1_element

            if selected_move == 2:
                move = self.move2
                ap = self.move2ap
                move_stamina = self.move2_stamina
                can_use_move_flag = True
                move_element = self.move2_element

            if selected_move == 3:
                move = self.move3
                ap = self.move3ap
                move_stamina = self.move3_stamina
                can_use_move_flag = True
                move_element = self.move3_element
            
            if move_element == "WIND":
                is_wind_element = True
            if move_element == "RANGED" and move_stamina >= 30:
                ranged_attack = True
            if move_element == "PHYSICAL" and move_stamina >= 80:
                is_physical_element = True
            move_emoji = crown_utilities.set_emoji(move_element)

        if selected_move in ENHANCERS:
            enhancer = True
            enh = self.move4enh
            ap = self.move4ap
            move_stamina = self.move4_stamina
            move = self.move4

        if selected_move == 6:
            enhancer = True
            enh = self._summon_type
            ap = self._summon_power
            move_stamina = 15
            move = self._summon_ability_name


        if not (move_stamina - self.stamina) <= 0:
            can_use_move_flag = False
            response = {
            "DMG": 0, 
            "MESSAGE": "You do not have the stamina to use this move! Try another mvoe.", 
            "CAN_USE_MOVE": can_use_move_flag, 
            "ENHANCE": False, 
            "REPEL": False, 
            "ABSORB": False, 
            "ELEMENT": move_element}
            return response
        
        tier = self.tier
        atk = self.attack
        defense = self.defense
        stam = self.stamina
        hlt = self.health
        lifesteal = 0
        drain = 0
        growth = 0
        flog = 0
        wither = 0
        brace = 0
        rage = 0
        bzrk = 0
        crystal = 0
        stance = 0
        confuse = 0
        blink = 0
        slow = 0
        haste = 0
        soulchain = 0
        gamble = 0
        fear = 0
        wave = 0
        creation = 0
        blast = 0
        destruction = 0

        if enhancer:
            if enh == "ATK":
                enhancer_value = round((ap / 100) * atk)
            elif enh == "DEF":
                enhancer_value = round((ap / 100) * defense)
            elif enh == "STAM":
                enhancer_value = ap
            elif enh == "HLT":
                hlt = round(ap + (.16 * self.health))
                newhealth = hlt + self.health
                if self.health >= self.max_health:
                    enhancer_value = 0
                elif newhealth >= self.max_health:
                    enhancer_value = round(self.max_health - self.health)
                else:
                    enhancer_value = round(hlt)
            elif enh == 'LIFE':
                lifesteal = round(ap + (.09 * _opponent_card.health))
                newhealth = lifesteal + self.health
                if self.health >= self.max_health:
                    enhancer_value = 0
                elif newhealth >= self.max_health:
                    enhancer_value = round(self.max_health - self.health)
                else:
                    enhancer_value = round(lifesteal)
            elif enh == 'DRAIN':
                enhancer_value = ap
            elif enh == "FLOG":
                if _opponent_card.attack >= 2000:
                    _opponent_card.attack = 2000
                enhancer_value = round((ap / 100) * _opponent_card.attack)
            elif enh == "WITHER":
                if _opponent_card.defense >= 2000:
                    _opponent_card.defense = 2000
                enhancer_value = round((ap / 100) * _opponent_card.defense)
            elif enh == "RAGE":
                if self.defense >= 2000:
                    self.defense = 2000
                enhancer_value = round((ap / 100) * self.defense)
            elif enh == 'BRACE':
                if self.attack >= 2000:
                    self.attack = 2000
                enhancer_value = round((ap / 100) * self.attack)
            elif enh == 'BZRK':
                enhancer_value = round((ap / 100) * self.health)
            elif enh == "CRYSTAL":
                enhancer_value = round((ap / 100) * self.health)
            elif enh == "GROWTH":
                enhancer_value = ap
            elif enh == "STANCE":
                enhancer_value = self.attack + ap
            elif enh == 'CONFUSE':
                enhancer_value = _opponent_card.attack - ap
            elif enh == 'BLINK':
                enhancer_value = ap
            elif enh == "SLOW":
                enhancer_value = ap
            elif enh == "HASTE":
                enhancer_value = ap
            elif enh == "FEAR":
                enhancer_value = ap
            elif enh == 'SOULCHAIN':
                enhancer_value = ap
            elif enh == 'GAMBLE':
                enhancer_value = ap
            elif enh == 'WAVE':
                if _battle._is_turn == 0:
                    enhancer_value = ap
                else:
                    rand = round(random.randint(2, 50))
                    n = ap
                    if _battle._turn_total % 10 == 0:
                        n = ap
                    elif n <= 0:
                        n = 30
                    elif _battle._turn_total == rand:
                        n = ap * 2
                    else:
                        n = ap / _battle._turn_total
                    enhancer_value = n
            elif enh == 'BLAST':
                if _battle._is_turn == 0:
                    enhancer_value = ap
                else:
                    enhancer_value = round(ap * _battle._turn_total)
                    if enhancer_value >= (100 * tier):
                        enhancer_value = (100 * tier)
            elif enh == 'CREATION':
                if _battle._is_turn == 0:
                    enhancer_value = ap
                else:
                    rand = round(random.randint(2, 50))
                    n = ap
                    if _battle._turn_total % 10 == 0:
                        n = ap
                    elif n <= 0:
                        n = 30
                    elif _battle._turn_total == rand:
                        n = ap * 2
                    else:
                        n = ap / _battle._turn_total
                    enhancer_value = n
            elif enh == 'DESTRUCTION':
                if _battle._is_turn == 0:
                    enhancer_value = ap
                else:
                    enhancer_value = round(ap * _battle._turn_total)
                    if enhancer_value >= (100 * tier):
                        enhancer_value = (100 * tier)
                if enhancer_value > _opponent_card.health:
                    message = f'Opponent has been reduced.'
                    enhancer_value = _opponent_card.health - 1
            
            if enh == 'ATK':
                message = f'{move} used! Increasing Attack by {enhancer_value}'
            elif enh == 'DEF':
                message = f'{move} used! Increasing Defense by {enhancer_value}'
            elif enh == 'STAM':
                message = f'{move} used! Increasing Stamina by {enhancer_value}'
            elif enh == 'LIFE':
                if enhancer_value == 0:
                    message = f'{move} used! Stealing {enhancer_value} Health  Your Health is full!'
                else:
                    message = f'{move} used! Stealing {enhancer_value} Health'
            elif enh == 'DRAIN':
                message = f'{move} used! Draining {enhancer_value} Stamina'
            elif enh == 'FLOG':
                message = f'{move} used! Stealing {enhancer_value} Attack'
            elif enh == 'WITHER':
                message = f'{move} used! Stealing {enhancer_value} Defense'
            elif enh == 'RAGE':
                message = f'{move} used! Sacrificing {enhancer_value} Defense, Increasing AP by {enhancer_value}'
            elif enh == 'BRACE':
                message = f'{move} used! Sacrificing {enhancer_value} Attack, Increasing AP by {enhancer_value}'
            elif enh == 'BZRK':
                message = f'{move} used! Sacrificing {enhancer_value} Health, Increasing Attack by {enhancer_value}'
            elif enh == 'CRYSTAL':
                message = f'{move} used! Sacrifices {enhancer_value} Health, Increasing Defense by {enhancer_value}'
            elif enh == 'WAVE' or enh == 'BLAST':
                if enh == 'BLAST' and enhancer_value > (100 * tier):
                    enhancer_value =(100 * tier)
                message = f'{move} used! Dealing {round(enhancer_value)} {enh} Damage!'
            elif enh == 'CREATION':
                message = f'{move} used! Healing and Increasing Max Health by {round(enhancer_value)}'
            elif enh == 'DESTRUCTION':
                if enhancer_value > (100 * tier):
                    enhancer_value =(100 * tier)
                message = f'{move} used! Destroying {round(enhancer_value)} Max Health'
            elif enh == 'GROWTH':
                message = f'{move} used! Sacrificing 10% Max Health to Increase Attack, Defense and AP by {round(enhancer_value)}'
            elif enh == 'STANCE':
                message = f'{move} used! Swapping Attack and Defense, Increasing Defense to {enhancer_value}'
            elif enh == 'CONFUSE':
                message = f'{move} used! Swapping Opponent Attack and Defense, Decreasing Defense to {enhancer_value}'
            elif enh == 'HLT':
                if enhancer_value == 0:
                    message = f'{move} used! Healing for {enhancer_value} Health... Your Health is full!'
                else:
                    message = f'{move} used! Healing for {enhancer_value}!'
                message = f'{move} used! Healing for {enhancer_value}!'
            elif enh == 'FEAR':
                message = f'{move} used! Sacrificing 10% Max Health to Decrease Opponent Attack, Defense and AP by {round(enhancer_value)}'
            elif enh == 'SOULCHAIN':
                message = f'{move} used! Synchronizing Stamina to {enhancer_value}'
            elif enh == 'GAMBLE':
                message = f'{move} used! Synchronizing Health to {enhancer_value}'
            else:
                message = f'{move} used! Inflicts {enh}'

            
            self.stamina = self.stamina - move_stamina

            response = {"DMG": enhancer_value, "MESSAGE": message,
                        "CAN_USE_MOVE": can_use_move_flag, "ENHANCED_TYPE": enh, "ENHANCE": True, "STAMINA_USED": move_stamina}
            return response

        else:
            # Calculate Damage

            # dmg = ((int(ap) + int(atk)) / (op_defense + 2) * (.20 * int(ap)))
            try:
                defensepower = _opponent_card.defense - self.attack
                if defensepower <= 0:
                    defensepower = 1

                attackpower = (self.attack - _opponent_card.defense) + ap
                if attackpower<=0:
                    attackpower = ap

                abilitypower = round(attackpower / defensepower)
                if abilitypower <= 0:
                    abilitypower = 25

                dmg = abilitypower
                if self.attack >= (_opponent_card.defense * 2):
                    if dmg > (ap * 1.5):
                        dmg = ap * 1.5
                elif self.attack >=(_opponent_card.defense * 1.5):
                    if dmg > (ap * 1.2):  # If DMG > ap -> Dmg = ap * 1.2
                        dmg = ap * 1.2
                elif dmg < (ap / 2):  # If you dmg is less than you base AP you do / of AP Damage
                    if _opponent_card.defense >= (self.attack * 2):
                        dmg = ap / 3
                    else:
                        dmg = ap / 2

                # print(f'{turn} : {card}')
                # print("DEF:" , defensepower, "Closer to 1 is stronger op def")
                # print("ATK:" ,attackpower, "Higher is better")
                # print("AP:" , abilitypower)
                # print("DMG:", dmg)

                # fortitude = round((self.max_health - health))
                # print("FORT:" , fortitude)
                # print("****")
                # attackpower = round((int(atk) * int(ap)) / op_defense) #5.09
                # print(attackpower)
                # modifier = random.randint(6,11)
                # dmg = round((fortitude * attackpower))

                # dmg = ((attackpower * (100 * (100 / defensepower))) * .001) + int(ap)
                
                low = dmg - (dmg * .20)
                high = dmg + (dmg * .05)
                true_dmg = (round(random.randint(int(low), int(high)))) + 25

                message = ""            

                miss_hit = 2  # Miss
                low_hit = 6  # Lower Damage
                med_hit = 15  # Medium Damage
                standard_hit = 19  # Standard Damage
                high_hit = 20  # Crit Hit
                hit_roll = round(random.randint(0, 20))
                # print(f"HIT ROLL: {str(hit_roll)}")
                if move_element == "SPIRIT" and hit_roll >= 15:
                    hit_roll = hit_roll + 5
                    
                if self.universe == "Crown Rift Awakening" and hit_roll > med_hit:
                    hit_roll = hit_roll + 2
                
                if self.universe == "Crown Rift Slayers" and hit_roll <=low_hit:
                    hit_roll = hit_roll - 3

                if ranged_attack:
                    true_dmg = round(true_dmg * 1.7)

                if move_element == "RECOIL" and hit_roll > miss_hit:
                    true_dmg = round(true_dmg * 2.9)

                if is_wind_element and hit_roll > miss_hit:
                    _battle._wind_buff = round(_battle._wind_buff + round(true_dmg * .15))
                    true_dmg = round(true_dmg + _battle._wind_buff)

                if hit_roll < miss_hit:
                    if self.universe == 'Crown Rift Slayers':
                        true_dmg = round(true_dmg * 2.5)
                        message = f'🩸{move_emoji} Feint Attack! {move} Critically Hits for **{true_dmg}**!! :boom: '
                    elif is_wind_element:
                        true_dmg = round(true_dmg)
                        message = f'🌪️ Wind Attack! {move} hits for **{true_dmg}**!'       
                    else:
                        true_dmg = 0
                        message = f'{move_emoji} {move} misses! :dash:'
                
                elif hit_roll <= low_hit and hit_roll > miss_hit:
                    true_dmg = round(true_dmg * .70)
                    message = f'{move_emoji} {move} used! Chips for **{true_dmg}**! :anger:'
                
                elif hit_roll <= med_hit and hit_roll > low_hit:
                    true_dmg = round(true_dmg)
                    message = f'{move_emoji} {move} used! Connects for **{true_dmg}**! :bangbang:'
                
                elif hit_roll <= standard_hit and hit_roll > med_hit:
                    true_dmg = round(true_dmg * 1.2)
                    message = f'{move_emoji} {move} used! Hits for **{true_dmg}**! :anger_right:'
                
                elif hit_roll >= 20:
                    if self.universe =="Crown Rift Awakening":
                        true_dmg = round(true_dmg * 4)
                        message = f"🩸 {move_emoji} Blood Awakening! {move} used! Critically Hits for **{true_dmg}**!! :boom:"
                    else:
                        true_dmg = round(true_dmg * 2.5)
                        message = f"{move_emoji} {move} used! Critically Hits for **{true_dmg}**!! :boom:"
                else:
                    message = f"{move_emoji} {move} used! Dealt **{true_dmg}** dmg!"


                if self.universe == "YuYu Hakusho":
                    additional_dmg = self.stamina + _battle._turn_total
                    true_dmg = round(true_dmg + additional_dmg)

                if is_physical_element:
                    if self.stamina > 80:
                        true_dmg = round(true_dmg * 3)

                if move_element in _opponent_card.weaknesses and not (hit_roll <= miss_hit):
                    true_dmg = round(true_dmg * 1.6)
                    message = f"Opponent is weak to {move_emoji} {move_element.lower()}! Strong hit for **{true_dmg}**!"

                if not _battle.is_ai_opponent:
                    if not _opponent_card._talisman == move_element and not _battle._is_boss:
                        if move_element in _opponent_card.resistances and not (hit_roll <= miss_hit) :
                            true_dmg = round(true_dmg * .45)
                            message = f"Opponent is resistant to {move_emoji} {move_element.lower()}. Weak hit for **{true_dmg}**!"

                        if move_element in _opponent_card.immunity and not (hit_roll <= miss_hit):
                            true_dmg = 0
                            message = f"Opponent is immune to {move_emoji} {move_element.lower()}. **0** dmg dealt!"

                        if move_element in _opponent_card.repels and not (hit_roll <= miss_hit):
                            message = f"Opponent repels {move_emoji} {move_element.lower()} for **{true_dmg}** dmg!"
                            does_repel = True
                        if move_element in _opponent_card.absorbs and not (hit_roll <= miss_hit):
                            message = f"Opponent absorbs {move_emoji} {move_element.lower()} for **{true_dmg}** dmg!"
                            does_absorb = True

                self.stamina = self.stamina - move_stamina

                response = {"DMG": true_dmg, "MESSAGE": message,
                            "CAN_USE_MOVE": can_use_move_flag, "ENHANCE": False, "REPEL": does_repel, "ABSORB": does_absorb, "ELEMENT": move_element, "STAMINA_USED": move_stamina}
                            
                return response

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


    def set_battle_arm_messages(self, opponent_card):
        if self.used_resolve:
            self.summon_resolve_message = f"🧬 {str(enhancer_mapping[self._summon_type])}"
        if opponent_card._barrier_active:
            opponent_card._arm_message = f"💠 {str(opponent_card._barrier_value)}"
        
        elif opponent_card._shield_active:
            opponent_card._arm_message = f"🌐 {str(opponent_card._shield_value)}"
        
        elif opponent_card._parry_active:
            opponent_card._arm_message = f"🔄 {str(opponent_card._parry_value)}"
        
        elif opponent_card._siphon_active:
            opponent_card._arm_message = f"💉 {str(opponent_card._siphon_value)}"
                
        if self._barrier_active:
            self._arm_message = f"💠 {str(self._barrier_value)} Barriers"

        elif self._shield_active:
            self._arm_message = f"🌐 {str(self._shield_value)} Shield"
                
        elif self._parry_active:
            self._arm_message = f"🔄 {str(self._parry_value)} Parries"
        
        elif self._siphon_active:
            self._arm_message = f"💉 {str(self._siphon_value)} Siphon"
        

    def focusing(self, _title, _opponent_title, _opponent_card, _battle, _co_op_card=None, _co_op_title=None ):
        if self.stamina < self.stamina_required_to_focus:
            self.used_focus = True
            if _battle._is_tutorial and _battle.tutorial_focus is False:
                # _opponent_card.used_focus = True
                embedVar = discord.Embed(title=f"You've entered :cyclone:**Focus State**!",
                                        description=f"Entering :cyclone:**Focus State** sacrifices a turn to **Heal** and regain **ST (Stamina)**!",
                                        colour=0xe91e63)
                embedVar.add_field(name=":cyclone:**Focusing**",
                                value="Increase **ATK** (🟦) and **DEF** (🟥)!")
                embedVar.set_footer(
                    text="Pay attention to your oppononets ST(Stamina). If they are entering Focus State, you will have the ability to strike twice!")
                
                _battle._tutorial_message = embedVar

            self.used_summon = False
            self.focus_count = self.focus_count + 1

            if _battle._is_boss:
                embedVar = discord.Embed(title=f"{_battle._punish_boss_description}")
                embedVar.add_field(name=f"{_battle._arena_boss_description}", value=f"{_battle._world_boss_description}", inline=False)
                embedVar.set_footer(text=f"{_battle._assault_boss_description}")
                _battle._boss_embed_message = embedVar
                

            # fortitude or luck is based on health
            fortitude = round(self.health * .1)
            if fortitude <= 50:
                fortitude = 50

            self.stamina = self.stamina_focus_recovery_amount
            health_calculation = round(fortitude)
            attack_calculation = round(fortitude * (self.tier / 10))
            defense_calculation = round(fortitude * (self.tier / 10))
            
            if self.universe == "One Piece" and (self.tier in crown_utilities.MID_TIER_CARDS or self.tier in crown_utilities.HIGH_TIER_CARDS):
                attack_calculation = attack_calculation + attack_calculation
                defense_calculation = defense_calculation + defense_calculation

            if _title.passive_type:
                if _title.passive_type == "GAMBLE":
                    health_calculation = _title.passive_value
                if _title.passive_type == "SOULCHAIN":
                    self.stamina = _title.passive_value
                    _opponent_card.stamina = _title.passive_value
                    if _battle._is_co_op:
                        _co_op_card.stamina = _title.passive_value
                if _title.passive_type == "BLAST":
                    _opponent_card.health = _opponent_card.health - (_title.passive_value * _battle.turn_total)

            if _opponent_title.passive_type:
                if _opponent_title.passive_type == "GAMBLE":
                    health_calculation = _opponent_title.passive_value
            
            if _battle._is_co_op:
                if _co_op_title.passive_type:
                    if _co_op_title.passive_type == "GAMBLE":
                        health_calculation = _co_op_title.passive_value

            new_health_value = 0
            heal_message = ""
            message_number = 0
            if self.universe == "Crown Rift Madness":
                heal_message = "yet inner **Madness** drags on..."
                message_number = 3
            else:
                if self.health <= self.max_health:
                    new_health_value = self.health + health_calculation
                    if new_health_value > self.max_health:
                        heal_message = "the injuries dissapeared!"
                        message_number = 1
                        self.health = self.max_health
                    else:
                        heal_message = "regained some vitality."
                        message_number = 2
                        self.health = new_health_value
                else:
                    heal_message = f"**{_opponent_card.name}**'s blows don't appear to have any effect!"
                    message_number = 0
            if not self.used_resolve:
                self.attack = self.attack + attack_calculation
                self.defense = self.defense + defense_calculation
            
            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🌀 **{self.name}** focused and {heal_message}")
            

            # Resolve Check and Calculation
            if not self.used_resolve and self.used_focus and self.universe == "Digimon":  # Digimon Universal Trait
                if _battle._is_tutorial and _opponent_card.used_resolve is False:
                    _opponent_card.used_resolve = True
                    embedVar = discord.Embed(title=f"⚡**Resolve Transformation**!",
                                            description=f"**Heal**, Boost **ATK**, and gain the ability to 🧬**Summon**!",
                                            colour=0xe91e63)
                    embedVar.add_field(name=f"Trade Offs!",
                                    value="Sacrifice **DEF** and **Focusing** will not increase **ATK** or **DEF**")
                    embedVar.add_field(name=f"🧬 Summons",
                                    value=f"🧬**Summons** will use their 🦠**Enhancers** to assist you in battle!")
                    embedVar.set_footer(
                        text=f"You can only enter ⚡Resolve once per match! Use the Heal Wisely!!!")
                    _battle.tutorial_message = embedVar

                
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve))
                resolve_attack_value = round((.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round((.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.attack = round(self.attack * 1.5)
                self.defense = round(self.defense * 1.5)
                self.used_resolve = True
                self.used_summon = False
                if _battle._turn_total <=5:
                    self.attack = round(self.attack * 2)
                    self.defense = round(self.defense * 2 )
                    self.health = self.health + 500
                    self.max_health = self.max_health + 500
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Transformation: Mega Digivolution!!!")
                else:
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Transformation: Digivolve")

            elif self.universe == "League Of Legends":                
                _opponent_card.health = round(_opponent_card.health - (60 + _battle._turn_total))
                
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🩸 Turret Shot hits **{_opponent_card.name}** for **{60 + _battle._turn_total}** Damage 💥")

            elif self.universe == "Dragon Ball Z":
                self.health = self.health + _opponent_card.stamina + _battle._turn_total
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🩸 Saiyan Spirit... You heal for **{_opponent_card.stamina + _battle._turn_total}** ❤️")

            elif self.universe == "Solo Leveling":
                _opponent_card.defense = round(_opponent_card.defense - (30 + _battle._turn_total))
                
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🩸 Ruler's Authority... Opponent loses **{30 + _battle._turn_total}** 🛡️ 🔻")
            
            elif self.universe == "Black Clover":                
                self.stamina = 100
                self.card_lvl_ap_buff = self.card_lvl_ap_buff + 50

                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🩸 Mana Zone! **{self.name}** Increased AP & Stamina 🌀")
            
            elif self.universe == "Death Note":
                if _battle._turn_total >= 100:
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{_opponent_card.name}** 🩸 had a heart attack and died")
                    
                    _opponent_card.health = 0

            if _opponent_card.universe == "One Punch Man" and self.universe != "Death Note":
                _opponent_card.health = round(_opponent_card.health + 100)
                _opponent_card.max_health = round(_opponent_card.max_health + 100)

                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🩸 Hero Reinforcements! **{_opponent_card.name}**  Increased Health & Max Health ❤️")

            elif _opponent_card.universe == "7ds":
                _opponent_card.stamina = _opponent_card.stamina + 60
                _opponent_card.used_summon = False
                
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🩸 Power Of Friendship! 🧬 {_opponent_card.name} Summon Rested, **{_opponent_card.name}** Increased Stamina 🌀")
            
            elif _opponent_card.universe == "Souls":
                _opponent_card.attack = round(_opponent_card.attack + (60 + _battle._turn_total))

                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🩸 Combo Recognition! **{_opponent_card.name}** Increased Attack by **{60 + _battle._turn_total}** 🔺")
            
            else:
                _battle._turn_total = _battle._turn_total + 1
                if self.universe != "Crown Rift Madness":
                    _battle.next_turn()
                else:
                    _battle.repeat_turn()
            _battle._turn_total = _battle._turn_total + 1
            if self.universe != "Crown Rift Madness":
                _battle.next_turn()
            else:
                _battle.repeat_turn()


    def resolving(self, _battle, opponent_card, player=None, opponent=None):
        if not self.used_resolve and self.used_focus:
            if self.universe == "My Hero Academia":  # My Hero Trait
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                self.card_lvl_ap_buff = self.card_lvl_ap_buff + 200 + _battle._turn_total

                self.stamina = 160
                self.health = self.health + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.used_resolve = True
                self.used_summon = False
                
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: PLUS ULTRA!")

                _battle._turn_total = _battle._turn_total + 1
                _battle.repeat_turn()

            if self.universe == "One Piece" and (self.name_tier in crown_utilities.HIGH_TIER_CARDS):
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                opponent_card.card_lvl_ap_buff = opponent_card.card_lvl_ap_buff - 125

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.used_resolve = True
                self.used_summon = False

                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: Conquerors Haki!")

                _battle._turn_total = _battle._turn_total + 1
                _battle._next_turn()


            elif self.universe == "Demon Slayer": 
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))


                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                if opponent_card.attack > self.attack:
                    self.attack = opponent_card.attack
                if opponent_card.defense > self.defense:
                    self.defense = opponent_card.defense
                self.used_resolve = True
                self.used_summon = False

                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: Total Concentration Breathing!")
                _battle._turn_total = _battle._turn_total + 1
                _battle._next_turn()

            elif self.universe == "Naruto": 
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.health = self.health + o_naruto_heal_buff
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)

                self.used_resolve = True
                self.used_summon = False

                _battle._turn_total = _battle._turn_total + 1
                _battle.next_turn()

            elif self.universe == "Attack On Titan":
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.used_resolve = True
                self.used_summon = False
                health_boost = 100 * self.focus_count
                self.health = self.health + health_boost

                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: Titan Mode! Health increased by **{health_boost}**!")

                _battle._turn_total = _battle._turn_total + 1
                _battle.next_turn()

            elif self.universe == "Bleach":  # Bleach Trait
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.attack = round((self.attack + (2 * resolve_attack_value))* 2)
                self.defense = round(self.defense - resolve_defense_value)
                # if self.defense >= 120:
                # # self.defense = 120
                self.used_resolve = True
                self.used_summon = False
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: Bankai!")

                _battle._turn_total = _battle._turn_total + 1
                _battle.next_turn()
            
            elif self.universe == "God Of War":  # God Of War Trait
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.used_resolve = True
                self.used_summon = False

                if self._gow_resolve:
                    self.health = self.max_health
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{opponent_card.name}** 🩸 Resolved: Ascension!")
                elif not self._gow_resolve:
                    self.health = round(self.health + (self.max_health / 2))
                    self.used_resolve = False
                    self._gow_resolve = True
                    
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Crushed Blood Orb: Health Refill")
                                
                _battle._turn_total = _battle._turn_total + 1
                _battle.next_turn()
            
            elif self.universe == "Fate":  # Fate Trait
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                
                damage_calculation_response = self.damage_cal(3, _battle, opponent_card, )
                opponent_card.health = opponent_card.health - damage_calculation_response['DMG']

                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: Command Seal!")

                # self.stamina = 0
                self.used_resolve = True
                self.used_summon = False
                _battle._turn_total = _battle._turn_total + 1
                _battle.next_turn()
            
            elif self.universe == "Kanto Region" or self.universe == "Johto Region" or self.universe == "Hoenn Region" or self.universe == "Sinnoh Region" or self.universe == "Kalos Region" or self.universe == "Unova Region" or self.universe == "Alola Region" or self.universe == "Galar Region":  # Pokemon Resolves
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = self.defense * 2
                self.used_resolve = True
                self.used_summon = False

                if turn_total >= 50:
                    self.max_health = self.max_health + 1000
                    self.health = self.health + 1000
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: Gigantomax Evolution!!! Gained **1000** HP!!!")
                elif turn_total >= 30:
                    self.max_health = self.max_health + 500
                    self.health = self.health + 500
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: Mega Evolution!! Gained **500** HP!")
                else:
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: Evolution!")

                _battle._turn_total = _battle._turn_total + 1
                _battle.next_turn()
            else:  # Standard Resolve
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.used_resolve = True
                self.used_summon = False
                if self.universe == "League Of Legends":
                    opponent_card.health = opponent_card.health - (60 * (self.focus_count + opponent_card.focus_count))
                
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Resolved: Pentakill! Dealing {(60 * (self.focus_count + opponent_card.focus_count))} damage.")
                elif self.universe == "Souls":
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Phase 2: Enhanced Moveset!")
                else:
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) ⚡ **{self.name}** Resolved!")

                _battle._turn_total = _battle._turn_total + 1
                _battle.next_turn()

            if _battle._is_boss:
                embedVar.add_field(name=f"{opponent_card.name}'s Rebuke", value=f"{_battle._rebuke_boss_description}",
                                inline=False)
                embedVar.set_footer(text=f"{self.name} this is your chance!")
                _battle._boss_embed_message = embedVar
    

    def use_summon(self, _battle, opponent_card):
        if self.used_resolve and self.used_focus and not self.used_summon:
            self.enhancer_used = True
            damage_calculation_response = self.damage_cal(6, _battle, opponent_card)
            self.enhancer_used = False
            self.used_summon = True
            if damage_calculation_response['CAN_USE_MOVE']:
                if self._summon_type == 'ATK':
                    self.attack = round(self.attack + damage_calculation_response['DMG'])
                elif self._summon_type == 'DEF':
                    self.defense = round(self.defense + damage_calculation_response['DMG'])
                elif self._summon_type == 'STAM':
                    self.stamina = round(self.stamina + damage_calculation_response['DMG'])
                elif self._summon_type == 'HLT':
                    self.health = round(self.health + damage_calculation_response['DMG'])
                elif self._summon_type == 'LIFE':
                    self.health = round(self.health + damage_calculation_response['DMG'])
                    opponent_card.health = round(opponent_card.health - damage_calculation_response['DMG'])
                elif self._summon_type == 'DRAIN':
                    self.stamina = round(self.stamina + damage_calculation_response['DMG'])
                    opponent_card.stamina = round(opponent_card.stamina - damage_calculation_response['DMG'])
                elif self._summon_type == 'FLOG':
                    self.attack = round(self.attack + damage_calculation_response['DMG'])
                    opponent_card.attack = round(opponent_card.attack - damage_calculation_response['DMG'])
                elif self._summon_type == 'WITHER':
                    self.defense = round(self.defense + damage_calculation_response['DMG'])
                    opponent_card.defense = round(opponent_card.defense - damage_calculation_response['DMG'])
                elif self._summon_type == 'RAGE':
                    self.defense = round(self.defense - damage_calculation_response['DMG'])
                    self.card_lvl_ap_buff = round(self.card_lvl_ap_buff + damage_calculation_response['DMG'])
                elif self._summon_type == 'BRACE':
                    self.card_lvl_ap_buff = round(self.card_lvl_ap_buff + damage_calculation_response['DMG'])
                    self.attack = round(self.attack - damage_calculation_response['DMG'])
                elif self._summon_type == 'BZRK':
                    self.health = round(self.health - damage_calculation_response['DMG'])
                    self.attack = round(self.attack + damage_calculation_response['DMG'])
                elif self._summon_type == 'CRYSTAL':
                    self.health = round(self.health - damage_calculation_response['DMG'])
                    self.defense = round(self.defense + damage_calculation_response['DMG'])
                elif self._summon_type == 'GROWTH':
                    self.max_health = round(self.max_health - (self.max_health * .10))
                    self.defense = round(self.defense + damage_calculation_response['DMG'])
                    self.attack= round(self.attack + damage_calculation_response['DMG'])
                    self.card_lvl_ap_buff = round(self.card_lvl_ap_buff + damage_calculation_response['DMG'])
                elif self._summon_type == 'STANCE':
                    tempattack = damage_calculation_response['DMG']
                    self.attack = self.defense
                    self.defense = tempattack
                elif self._summon_type == 'CONFUSE':
                    tempattack = damage_calculation_response['DMG']
                    opponent_card.attack = opponent_card.defense
                    opponent_card.defense = tempattack
                elif self._summon_type == 'BLINK':
                    self.stamina = round(self.stamina - damage_calculation_response['DMG'])
                    opponent_card.stamina = round(opponent_card.stamina + damage_calculation_response['DMG'])
                elif self._summon_type == 'SLOW':
                    tempstam = round(opponent_card.stamina + damage_calculation_response['DMG'])
                    self.stamina = round(self.stamina - damage_calculation_response['DMG'])
                    opponent_card.stamina = self.stamina
                    self.stamina = tempstam
                elif self._summon_type == 'HASTE':
                    tempstam = round(opponent_card.stamina - damage_calculation_response['DMG'])
                    self.stamina = round(self.stamina + damage_calculation_response['DMG'])
                    opponent_card.stamina = self.stamina
                    self.stamina = tempstam
                elif self._summon_type == 'SOULCHAIN':
                    self.stamina = round(damage_calculation_response['DMG'])
                    opponent_card.stamina = self.stamina
                elif self._summon_type == 'GAMBLE':
                    self.health = round(damage_calculation_response['DMG'])
                    opponent_card.health = self.health
                elif self._summon_type == 'FEAR':
                    if self.universe != "Chainsawman":
                        self.max_health = round(self.max_health - (self.max_health * .10))
                    opponent_card.defense = round(opponent_card.defense - damage_calculation_response['DMG'])
                    opponent_card.attack= round(opponent_card.attack - damage_calculation_response['DMG'])
                    opponent_card.card_lvl_ap_buff = round(opponent_card.card_lvl_ap_buff - damage_calculation_response['DMG'])
                elif self._summon_type == 'WAVE':
                    opponent_card.health = round(opponent_card.health - damage_calculation_response['DMG'])
                elif self._summon_type == 'BLAST':
                    if damage_calculation_response['DMG'] >= 300:
                        damage_calculation_response['DMG'] = 300
                    opponent_card.health = round(opponent_card.health - damage_calculation_response['DMG'])
                elif self._summon_type == 'CREATION':
                    self.max_health = round(self.max_health + damage_calculation_response['DMG'])
                    self.health = round(self.health + damage_calculation_response['DMG'])
                elif self._summon_type == 'DESTRUCTION':
                    if damage_calculation_response['DMG'] >= 300:
                        damage_calculation_response['DMG'] = 300
                    opponent_card.max_health = round(opponent_card.max_health - damage_calculation_response['DMG'])
                    if opponent_card.max_health <=1:
                        opponent_card.max_health = 1

                if self.universe == "Persona":
                    petdmg = self.damage_cal(1, _battle, opponent_card)
                    opponent_card.health = opponent_card.health - petdmg['DMG']

                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **Persona!** 🩸 : **{self._summon_name}** was summoned from **{self.name}'s** soul dealing **{petdmg['DMG']}** damage!\n**{opponent_card.name}** summon disabled!")
                    opponent_card.used_summon = True
                else:
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** Summoned 🧬 **{self._summon_name}**: {damage_calculation_response['MESSAGE']}")
                _battle.repeat_turn()
                return damage_calculation_response
            else:
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🧬 **{self._summon_name}** needs a turn to rest...")
                _battle.repeat_turn()
        else:
            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🧬 **{self._summon_name}** needs a turn to rest...")
            _battle.repeat_turn()

    
    def set_talisman(self, _battle):
        # if normal, apply talisman for basic attack
        # if hard, apply talisman for ultimate attack
        if _battle._is_normal:
            self._talisman = self.move1_element
        
        if _battle._is_hard:
            self._talisman = self.move3_element 

        if not self._talisman:
            self._talisman = "None"


    def use_companion_enhancer(self, _battle, opponent_card, companion_card):
        self.enhancer_used = True
        dmg = self.damage_cal(6, _battle, companion_card)
        self.enhancer_used = False

        if dmg['CAN_USE_MOVE']:
            if companion_card.move4enh == 'ATK':
                companion_card.attack = round(companion_card.attack + dmg['DMG'])
            elif companion_card.move4enh == 'DEF':
                companion_card.defense = round(companion_card.defense + dmg['DMG'])
            elif companion_card.move4enh == 'STAM':
                companion_card.stamina = round(companion_card.stamina + dmg['DMG'])
            elif companion_card.move4enh == 'HLT':
                companion_card.health = round(companion_card.health + dmg['DMG'])
            elif companion_card.move4enh == 'LIFE':
                companion_card.health = round(companion_card.health + dmg['DMG'])
                self.health = round(self.health - dmg['DMG'])
            elif companion_card.move4enh == 'DRAIN':
                companion_card.stamina = round(companion_card.stamina + dmg['DMG'])
                player1_card.stamina = round(player1_card.stamina - dmg['DMG'])
            elif companion_card.move4enh == 'FLOG':
                companion_card.attack = round(companion_card.attack + dmg['DMG'])
                opponent_card.attack = round(self.attack - dmg['DMG'])
            elif companion_card.move4enh == 'WITHER':
                companion_card.defense = round(companion_card.defense + dmg['DMG'])
                opponent_card.defense = round(self.defense - dmg['DMG'])
            elif companion_card.move4enh == 'RAGE':
                companion_card.defense = round(companion_card.defense - dmg['DMG'])
                companion_card.card_lvl_ap_buff = round(companion_card.card_lvl_ap_buff + dmg['DMG'])
            elif companion_card.move4enh == 'BRACE':
                companion_card.card_lvl_ap_buff = round(companion_card.card_lvl_ap_buff + dmg['DMG'])
                companion_card.attack = round(companion_card.attack - dmg['DMG'])
            elif companion_card.move4enh == 'BZRK':
                companion_card.health = round(companion_card.health - dmg['DMG'])
                companion_card.attack = round(companion_card.attack + dmg['DMG'])
            elif companion_card.move4enh == 'CRYSTAL':
                companion_card.health = round(companion_card.health - dmg['DMG'])
                companion_card.defense = round(companion_card.defense + dmg['DMG'])
            elif companion_card.move4enh == 'GROWTH':
                companion_card.max_health = round(companion_card.max_health - (companion_card.max_health * .10))
                companion_card.defense = round(companion_card.defense + dmg['DMG'])
                companion_card.attack = round(companion_card.attack + dmg['DMG'])
                companion_card.card_lvl_ap_buff = round(companion_card.card_lvl_ap_buff + dmg['DMG'])
            elif companion_card.move4enh == 'STANCE':
                tempattack = dmg['DMG']
                companion_card.attack = companion_card.defense
                companion_card.defense = tempattack
            elif companion_card.move4enh == 'CONFUSE':
                tempattack = dmg['DMG']
                self.attack = self.defense
                self.defense = tempattack
            elif companion_card.move4enh == 'BLINK':
                companion_card.stamina = round(companion_card.stamina - dmg['DMG'])
                player1_card.stamina = round(player1_card.stamina + dmg['DMG'])
            elif companion_card.move4enh == 'SLOW':
                tempstam = round(player1_card.stamina + dmg['DMG'])
                companion_card.stamina = round(companion_card.stamina - dmg['DMG'])
                player1_card.stamina = companion_card.stamina
                companion_card.stamina = tempstam
            elif companion_card.move4enh == 'HASTE':
                tempstam = round(player1_card.stamina - dmg['DMG'])
                companion_card.stamina = round(companion_card.stamina + dmg['DMG'])
                player1_card.stamina = companion_card.stamina
                companion_card.stamina = tempstam
            elif companion_card.move4enh == 'SOULCHAIN':
                companion_card.stamina = round(dmg['DMG'])
                player1_card.stamina = companion_card.stamina
            elif companion_card.move4enh == 'GAMBLE':
                companion_card.health = round(dmg['DMG'])
                self.health = companion_card.health
            elif companion_card.move4enh == 'FEAR':
                if companion_card.universe != "Chainsawman":
                    companion_card.max_health = round(companion_card.max_health - (companion_card.max_health * .10))
                opponent_card.defense = round(opponent_card.defense - dmg['DMG'])
                opponent_card.attack= round(opponent_card.attack - dmg['DMG'])
                opponent_card.card_lvl_ap_buff = round(opponent_card.card_lvl_ap_buff - dmg['DMG'])
            elif companion_card.move4enh == 'WAVE':
                opponent_card.health = round(opponent_card.health - dmg['DMG'])
            elif companion_card.move4enh == 'BLAST':
                if dmg['DMG'] >= 500:
                    dmg['DMG'] = 500
                opponent_card.health = round(opponent_card.health - dmg['DMG'])
            elif companion_card.move4enh == 'CREATION':
                companion_card.max_health = round(companion_card.max_health + dmg['DMG'])
                companion_card.health = round(companion_card.health + dmg['DMG'])
            elif companion_card.move4enh == 'DESTRUCTION':
                opponent_card.max_health = round(opponent_card.max_health - dmg['DMG'])
                if opponent_card.max_health <=1:
                    opponent_card.max_health = 1

            if companion_card.move4enh in crown_utilities.Stamina_Enhancer_Check or companion_card.move4enh in crown_utilities.Time_Enhancer_Check:
                opponent_card.stamina = opponent_card.stamina

            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** used {player1_card.move4}:👥 Assisting **{companion_card.name}**")
            _battle._turn_total = _battle_turn_total + 1
            _battle.next_turn()
        else:
            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) {self.name} doesn't have enough Stamina to use this move")
            _battle.repeat_turn()


    def use_block(self, _battle, opponent_card, co_op_card=None):
        if self.stamina >= 20:
            if self.universe == "Attack On Titan":
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **Rally** 🩸 ! **{self.name}** Increased Max Health ❤️")
                self.max_health = round(self.max_health + 100)
                self.health = self.health + 100

            if self.universe == "Black Clover":                
                self.stamina = self.stamina + 50
                self.card_lvl_ap_buff = self.card_lvl_ap_buff + 30
                print(f"AP BUFF IS: {self.card_lvl_ap_buff}")
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Charged their mana, increasing their mana & ap by 30")

            if self.universe == "Bleach":
                dmg = self.damage_cal(1, _battle, opponent_card)
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** Exerted their 🩸 Spiritual Pressure - {dmg['MESSAGE']}")
                if self.universe == "One Piece" and (self.name_tier in crown_utilities.LOW_TIER_CARDS or self.name_tier in crown_utilities.MID_TIER_CARDS or self.name_tier in crown_utilities.HIGH_TIER_CARDS):
                    if self.focus_count == 0:
                        dmg['DMG'] = dmg['DMG'] * .6
                
                self.activate_element_check(_battle, dmg, opponent_card)

            if _battle._is_co_op:
                block_message = f"**{self.name}**: Defended 🛡️ **{co_op_card.name}**"
                self.used_defend = True
            else:
                block_message = f"**{self.name}** Blocked 🛡️"
                self.used_block = True
            self.stamina = self.stamina - 20
            self.defense = round(self.defense * 2)

            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) {block_message}")
            _battle._turn_total = _battle._turn_total + 1
            _battle.next_turn()
        else:
            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** is too tired to block.")
            _battle.repeat_turn()

    
    def use_defend(self, _battle, companion_card):
        if self.stamina >= 20:
            self.used_defend = True
            self.stamina = self.stamina - 20
            self.defense = round(self.defense * 2)
            
            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**: Defended 🛡️ **{companion_card.name}**")
            _battle._turn_total = _battle._turn_total + 1
            _battle.next_turn()
        else:
            #await private_channel.send(f"{c_card} is too tired to block...")
            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** is too tired to block.")
            _battle.repeat_turn()
    


    def damage_done(self, _battle, dmg, opponent_card):
        if dmg['CAN_USE_MOVE']:
            if dmg['ENHANCE']:
                if self.move4enh == 'ATK':
                    self.attack = round(self.attack + dmg['DMG'])
                elif self.move4enh == 'DEF':
                    self.defense = round(self.defense + dmg['DMG'])
                elif self.move4enh == 'STAM':
                    self.stamina = round(self.stamina + dmg['DMG'])
                elif self.move4enh == 'HLT':
                    self.max_health = round(self.max_health + dmg['DMG'])
                elif self.move4enh == 'LIFE':
                    self.max_health = round(self.max_health + dmg['DMG'])
                    opponent_card.health = round(opponent_card.health - dmg['DMG'])
                elif self.move4enh == 'DRAIN':
                    self.stamina = round(self.stamina + dmg['DMG'])
                    opponent_card.stamina = round(opponent_card.stamina - dmg['DMG'])
                elif self.move4enh == 'FLOG':
                    self.attack = round(self.attack + dmg['DMG'])
                    opponent_card.attack = round(opponent_card.attack - dmg['DMG'])
                elif self.move4enh == 'WITHER':
                    self.defense = round(self.defense + dmg['DMG'])
                    opponent_card.defense = round(opponent_card.defense - dmg['DMG'])
                elif self.move4enh == 'RAGE':
                    self.defense = round(self.defense - dmg['DMG'])
                    self.card_lvl_ap_buff = round(self.card_lvl_ap_buff + dmg['DMG'])
                elif self.move4enh == 'BRACE':
                    self.card_lvl_ap_buff = round(self.card_lvl_ap_buff + dmg['DMG'])
                    self.attack = round(self.attack - dmg['DMG'])
                elif self.move4enh == 'BZRK':
                    self.max_health = round(self.max_health - dmg['DMG'])
                    self.attack = round(self.attack + dmg['DMG'])
                elif self.move4enh == 'CRYSTAL':
                    self.max_health = round(self.max_health - dmg['DMG'])
                    self.defense = round(self.defense + dmg['DMG'])
                elif self.move4enh == 'GROWTH':
                    self.max_health = round(self.max_health - (self.max_health * .10))
                    self.defense = round(self.defense + dmg['DMG'])
                    self.attack= round(self.attack + dmg['DMG'])
                    self.card_lvl_ap_buff = round(self.card_lvl_ap_buff + dmg['DMG'])
                elif self.move4enh == 'STANCE':
                    tempattack = dmg['DMG']
                    self.attack = self.defense
                    self.defense = tempattack
                elif self.move4enh == 'CONFUSE':
                    tempattack = dmg['DMG']
                    opponent_card.attack = opponent_card.defense
                    opponent_card.defense = tempattack
                elif self.move4enh == 'BLINK':
                    self.stamina = round(self.stamina - dmg['DMG'])
                    opponent_card.stamina = round(opponent_card.stamina + dmg['DMG'])
                elif self.move4enh == 'SLOW':
                    tempstam = round(opponent_card.stamina + dmg['DMG'])
                    self.stamina = round(self.stamina - dmg['DMG'])
                    opponent_card.stamina = self.stamina
                    self.stamina = tempstam
                elif self.move4enh == 'HASTE':
                    tempstam = round(opponent_card.stamina - dmg['DMG'])
                    self.stamina = round(self.stamina + dmg['DMG'])
                    opponent_card.stamina = self.stamina
                    self.stamina = tempstam
                elif self.move4enh == 'SOULCHAIN':
                    self.stamina = round(dmg['DMG'])
                    opponent_card.stamina = self.stamina
                elif self.move4enh == 'GAMBLE':
                    if _battle._is_dungeon:
                        opponent_card.health = round(dmg['DMG']) * 2
                        self.max_health = round(dmg['DMG'])
                    elif _battle._is_boss:
                        opponent_card.health = round(dmg['DMG']) * 3
                        self.max_health = round(dmg['DMG'])
                    else:
                        opponent_card.health = round(dmg['DMG'])
                        self.max_health = round(dmg['DMG'])
                elif self.move4enh == 'FEAR':
                    if self.universe != "Chainsawman":
                        self.max_health = round(self.max_health - (self.max_health * .10))
                    opponent_card.defense = round(opponent_card.defense - dmg['DMG'])
                    opponent_card.attack= round(opponent_card.attack - dmg['DMG'])
                    opponent_card.card_lvl_ap_buff = round(opponent_card.card_lvl_ap_buff - dmg['DMG'])
                elif self.move4enh == 'WAVE':
                    opponent_card.health = round(opponent_card.health - dmg['DMG'])
                elif self.move4enh == 'BLAST':
                    if dmg['DMG'] >= 700:
                        dmg['DMG'] = 700
                    opponent_card.health = round(opponent_card.health - dmg['DMG'])
                elif self.move4enh == 'CREATION':
                    self.max_health = round(self.max_health + dmg['DMG'])
                    self.max_health = round(self.max_health + dmg['DMG'])
                elif self.move4enh == 'DESTRUCTION':
                    opponent_card.max_health = round(opponent_card.max_health - dmg['DMG'])
                    if opponent_card.max_health <=1:
                        opponent_card.max_health = 1

                if self.move4enh in crown_utilities.Stamina_Enhancer_Check or self.move4enh in crown_utilities.Time_Enhancer_Check or self.move4enh in crown_utilities.Control_Enhancer_Check:
                    self.stamina = self.stamina

                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**: 🦠 {dmg['MESSAGE']}")
                _battle._turn_total = _battle._turn_total + 1
                _battle.next_turn()
                # await button_ctx.defer(ignore=True)
            elif dmg['DMG'] == 0:
                if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                    self._barrier_active = False
                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")
                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**: {dmg['MESSAGE']}")
                _battle._turn_total = _battle._turn_total + 1
                _battle.next_turn()
                
            else:
                if opponent_card.universe == "Naruto" and opponent_card.stamina < 10:
                    stored_damage = round(dmg['DMG'])
                    opponent_card._naruto_heal_buff = opponent_card._naruto_heal_buff + stored_damage
                    opponent_card.health = opponent_card.health 

                    if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                        self._barrier_active = False
                        _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")

                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{opponent_card.name}** 🩸: Substitution Jutsu")
                    if not opponent_card.used_resolve:
                        _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🩸**{stored_damage}** Hasirama Cells stored. 🩸**{opponent_card._naruto_heal_buff}** total stored.")
                
                elif opponent_card._shield_active and dmg['ELEMENT'] != "DARK":
                    if dmg['ELEMENT'] == "POISON": #Poison Update
                        if self.poison_dmg <= 600:
                            self.poison_dmg = self.poison_dmg + 30
                        
                    if opponent_card._shield_value > 0:
                        opponent_card._shield_value = opponent_card._shield_value - dmg['DMG']
                        opponent_card.health = opponent_card.health 
                        if opponent_card._shield_value <= 0:
                            residue_damage = opponent_card._shield_value
                            opponent_card.health = opponent_card.health - residue_damage
                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 🌐**{opponent_card.name}'s**: Shield Shattered and they were hit with **{str(abs(residue_damage))} DMG!**")
                            if opponent_card._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                                opponent_card._barrier_active = False
                                opponent_card._arm_message = ""
                                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")
                            opponent_card._shield_active = False
                        else:
                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** strikes **{opponent_card.name}**'s Shield 🌐\n**{opponent_card._shield_value} Shield** Left!")
                            if opponent_card._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                                opponent_card._barrier_active = False
                                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")

                elif opponent_card._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                    if opponent_card._barrier_value >1:
                        opponent_card.health = opponent_card.health 
                        _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{opponent_card.name}** Activates Barrier 💠 {self.name}'s attack **Nullified**!\n **{opponent_card._barrier_value - 1} Barriers** remain!")
                        if opponent_card._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                            opponent_card._barrier_active = False
                            opponent_card._arm_message = ""
                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")
                        opponent_card._barrier_value = opponent_card._barrier_value - 1
                    elif opponent_card._barrier_value==1:
                        _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{opponent_card.name}**'s Barrier Broken!")
                        opponent_card._barrier_value = opponent_card._barrier_value - 1
                        if opponent_card._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                            opponent_card._barrier_active = False
                            opponent_card._arm_message = ""
                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")
                        opponent_card._barrier_active = False
                
                elif opponent_card._parry_active and dmg['ELEMENT'] not in ["EARTH", "DARK", "PSYCHIC"]:                    
                    if opponent_card._parry_value > 1:
                        opponent_card.health = opponent_card.health
                        parry_damage = round(dmg['DMG'])
                        opponent_card.health = round(opponent_card.health - (parry_damage * .75))
                        self.max_health = round(self.max_health - (parry_damage * .40))
                        opponent_card._parry_value = opponent_card._parry_value - 1
                        _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{opponent_card.name}** Activates Parry 🔄 after **{round(parry_damage * .75)}** dmg dealt:  {self.name} takes {round(parry_damage * .40)}! DMG\n **{opponent_card._parry_value} Parries** to go!!")
                        if opponent_card._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                            opponent_card._barrier_active = False
                            opponent_card._arm_message = ""
                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")
                        
                    elif opponent_card._parry_value == 1:
                        opponent_card.health = opponent_card.health
                        parry_damage = round(dmg['DMG'])
                        opponent_card.health = round(opponent_card.health - (parry_damage * .75))
                        self.max_health = round(self.max_health - (parry_damage * .40))
                        _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{opponent_card.name}** Parry Penetrated! **{self.name}** takes **{round(parry_damage * .40)}**! DMG and breaks the **Parry**")
                        opponent_card._parry_value = opponent_card._parry_value - 1
                        if opponent_card._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                            opponent_card._barrier_active = False
                            opponent_card._arm_message = ""
                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")
                        opponent_card._parry_active = False
                
                else:
                    if self.universe == "One Piece" and (self.name_tier in crown_utilities.LOW_TIER_CARDS or self.name_tier in crown_utilities.MID_TIER_CARDS or self.name_tier in crown_utilities.HIGH_TIER_CARDS):
                        if self.focus_count == 0:
                            dmg['DMG'] = dmg['DMG'] * .6

                    if self._siphon_active:
                        siphon_damage = (dmg['DMG'] * .15) + self._siphon_value
                        self.max_health = round(self.max_health + siphon_damage)
                        if self.max_health >= self.max_health:
                            self.max_health = self.max_health
                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**: 💉 Siphoned **Full Health!**")
                        else:
                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**: 💉 Siphoned **{round(siphon_damage)}** Health!")
                    
                    if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                        self._barrier_active = False
                        _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")

                    self.activate_element_check(_battle, dmg, opponent_card)

                    _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}:** {dmg['MESSAGE']}")
                
                if opponent_card.health <= 0:
                    if opponent_card._final_stand==True:
                        if opponent_card.universe == "Dragon Ball Z":
                            if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                                self._barrier_active = False
                                _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**'s 💠 Barrier Disabled!")
                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{opponent_card.name}** 🩸 Transformation: Last Stand!!!")
                            opponent_card.health = int(.75 * (opponent_card.attack + opponent_card.defense))
                            
                            opponent_card.used_resolve = True
                            opponent_card.used_focus = True
                            opponent_card._final_stand = False
                            _battle._turn_total = _battle._turn_total + 1
                            _battle.next_turn()
                    else:
                        opponent_card.health = 0
                        _battle._turn_total = _battle._turn_total + 1
                else:
                    _battle._turn_total = _battle._turn_total + 1
                    _battle.next_turn()
                    
        else:
            print(f"End of damage_done")
            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**: Not enough Stamina to use this ability.")
            _battle.repeat_turn()


    def activate_element_check(self, _battle, dmg, opponent_card):
        if dmg['REPEL']:
            self.health = self.health - dmg['DMG']
        elif dmg['ABSORB']:
            opponent_card.health = opponent_card.health + dmg['DMG']

        if dmg['ELEMENT'] == "WATER":
            if self.move1_element == "WATER":
                self.basic_water_buff = self.basic_water_buff + 50
            if self.move2_element == "WATER":
                self.special_water_buff = self.special_water_buff + 50
            if self.move3_element == "WATER":
                self.ultimate_water_buff = self.ultimate_water_buff + 50
            opponent_card.health = opponent_card.health - dmg['DMG']
        
        elif dmg['ELEMENT'] == "TIME":
            if self.stamina <= 80:
                self.stamina = 0
            self.used_block = True
            self.defense = round(self.defense * 2)
            _battle._turn_total = _battle._turn_total + 1
            self.card_lvl_ap_buff = self.card_lvl_ap_buff + (dmg['DMG'] + (dmg['DMG'] / _battle._turn_total))
            _battle.add_battle_history_messsage(f"**{self.name}** Time has moved forward 3 turns!")
            opponent_card.health = opponent_card.health - (dmg['DMG'] * (_battle._turn_total / 100))

        elif dmg['ELEMENT'] == "EARTH":
            self.defense = self.defense + (dmg['DMG'] * .50)
            self._shield_active = True
            self._shield_value = self._shield_value * round(dmg['DMG'] * .50)
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "DEATH":
            opponent_card.max_health = opponent_card.max_health - (dmg['DMG'] * .45)
            self.attack = self.attack + (dmg['DMG'] * .45)
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "LIGHT":
            self.stamina = round(self.stamina + (dmg['STAMINA_USED'] / 2))
            self.attack = self.attack + (dmg['DMG'] * .45)
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "DARK":
            opponent_card.stamina = opponent_card.stamina - 20
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "PHYSICAL":
            self.physical_meter = self.physical_meter + 1
            if self.physical_meter == 2:
                self._parry_active = True
                self._parry_value = self._parry_value + 1
                self.physical_meter = 0
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "LIFE":
            self.max_health = self.max_health + (dmg['DMG'] * .35)
            self.health = self.health + (dmg['DMG'] * .40)
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "RECOIL":
            self.health = self.health - (dmg['DMG'] * .55)
            if self.health <= 0:
                self.health = 1
            opponent_card.health = opponent_card.health - dmg['DMG']


        elif dmg['ELEMENT'] == "PSYCHIC":
            opponent_card.defense = opponent_card.defense - (dmg['DMG'] * .30)
            opponent_card.attack = opponent_card.attack - (dmg['DMG'] * .30)
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "FIRE":
            self.burn_dmg = self.burn_dmg + round(dmg['DMG'] * .40)
            opponent_card.health = opponent_card.health - dmg['DMG']


        elif dmg['ELEMENT'] == "ELECTRIC":
            self.shock_buff = self.shock_buff +  (dmg['DMG'] * .30)
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "POISON":
            if self.poison_dmg <= 600:
                self.poison_dmg = self.poison_dmg + 30
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "ICE":
            self.ice_counter = self.ice_counter + 1
            if self.ice_counter == 2:
                self.freeze_enh = True
                self.ice_counter = 0
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "BLEED":
            self.bleed_damage_counter = self.bleed_damage_counter + 1
            if self.bleed_damage_counter == 2:
                self.bleed_hit = True
                self.bleed_damage_counter = 0
            opponent_card.health = opponent_card.health - dmg['DMG']
            
        elif dmg['ELEMENT'] == "GRAVITY":
            _battle._turn_total = _battle._turn_total - 2
            if (_battle._turn_total - 3) < 0:
                _battle.turn_total = 0
            self.gravity_hit = True
            opponent_card.health = opponent_card.health - dmg['DMG']
            opponent_card.defense = opponent_card.defense - (dmg['DMG'] * .75)
        
        else:
            opponent_card.health = opponent_card.health - dmg['DMG']
            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}**: {dmg['MESSAGE']}")


    def reset_stats_to_limiter(self, _opponent_card):
        if self.card_lvl_ap_buff > 700:
            self.card_lvl_ap_buff = 700
        
        if _opponent_card.card_lvl_ap_buff > 700:
            _opponent_card.card_lvl_ap_buff = 700
        
        if self.attack <= 25:
            self.attack = 25
        
        if self.defense <= 30:
            self.defense = 30
        
        if self.attack >= 9999:
            self.attack = 9999
        
        if self.defense >= 9999:
            self.defense = 9999
        
        if self.health >= self.max_health:
            self.health = self.max_health

        self.move1ap = list(self.m1.values())[0] + self.card_lvl_ap_buff + self.shock_buff + self.basic_water_buff + self.arbitrary_ap_buff
        self.move2ap = list(self.m2.values())[0] + self.card_lvl_ap_buff + self.shock_buff + self.basic_water_buff + self.arbitrary_ap_buff
        self.move3ap = list(self.m3.values())[0]+ self.card_lvl_ap_buff + self.shock_buff + self.basic_water_buff + self.arbitrary_ap_buff
        
        # _opponent_card.move1ap = _opponent_card.list(self.m1.values())[0] + _opponent_card.card_lvl_ap_buff + _opponent_card.shock_buff + _opponent_card.basic_water_buff + _opponent_card.arbitrary_ap_buff
        # _opponent_card.move2ap = _opponent_card.list(self.m2.values())[0] + _opponent_card.card_lvl_ap_buff + _opponent_card.shock_buff + _opponent_card.basic_water_buff + _opponent_card.arbitrary_ap_buff
        # _opponent_card.move3ap = _opponent_card.list(self.m3.values())[0] + _opponent_card.card_lvl_ap_buff + _opponent_card.shock_buff + _opponent_card.basic_water_buff + _opponent_card.arbitrary_ap_buff

    
    
    def yuyu_hakusho_attack_increase(self):
        self.attack = self.attack + self.stamina


    def activate_demon_slayer_trait(self, _battle, opponent_card):
        if self.universe == "Demon Slayer" and _battle._turn_total == 0 and not _battle._turn_zero_has_happened:
            _battle._turn_zero_has_happened = True
            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) **{self.name}** 🩸 Total Concentration Breathing: **Increased HP by {round(opponent_card.health * .40)}**")
            self.health = round(self.health + (opponent_card.health * .40))
            self.max_health = round(self.max_health + (opponent_card.health *.40))
    

    def activate_card_passive(self, player2_card):
        if self.passive_type:
            value_for_passive = self.tier * .5
            flat_value_for_passive = 10 * (self.tier * .5)
            stam_for_passive = 5 * (self.tier * .5)
            if self.passive_type == "HLT":
                if self.max_health > self.health:
                    self.health = round(round(self.health + ((value_for_passive / 100) * self.health)))
            if self.passive_type == "CREATION":
                self.max_health = round(round(self.max_health + ((value_for_passive / 100) * self.max_health)))
            if self.passive_type == "DESTRUCTION":
                player2_card.max_health = round(round(player2_card.max_health - ((value_for_passive / 100) * player2_card.max_health)))
            if self.passive_type == "LIFE":
                if self.max_health > self.health:
                    player2_card.health = round(player2_card.health - ((value_for_passive / 100) * player2_card.health))
                    self.health = round(self.health + ((value_for_passive / 100) * player2_card.health))
            if self.passive_type == "ATK":
                self.attack = round(self.attack + ((value_for_passive / 100) * self.attack))
            if self.passive_type == "DEF":
                self.defense = round(self.defense + ((value_for_passive / 100) * self.defense))
            if self.passive_type == "STAM":
                if self.stamina > 15:
                    self.stamina = self.stamina + stam_for_passive
            if self.passive_type == "DRAIN":
                if self.stamina > 15:
                    player2_card.stamina = player2_card.stamina - stam_for_passive
                    self.stamina = self.stamina + stam_for_passive
            if self.passive_type == "FLOG":
                player2_card.attack = round(player2_card.attack - ((value_for_passive / 100) * player2_card.attack))
                self.attack = round(self.attack + ((value_for_passive / 100) * player2_card.attack))
            if self.passive_type == "WITHER":
                player2_card.defense = round(player2_card.defense - ((value_for_passive / 100) * player2_card.defense))
                self.defense = round(self.defense + ((value_for_passive / 100) * player2_card.defense))
            if self.passive_type == "RAGE":
                self.defense = round(self.defense - ((value_for_passive / 100) * self.defense))
                self.card_lvl_ap_buff = round(self.card_lvl_ap_buff + ((value_for_passive / 100) * self.defense))
            if self.passive_type == "BRACE":
                self.card_lvl_ap_buff  = round(self.card_lvl_ap_buff + ((value_for_passive / 100) * self.attack))
                self.attack = round(self.attack - ((value_for_passive / 100) * self.attack))
            if self.passive_type == "BZRK":
                self.health = round(self.health - ((value_for_passive / 100) * self.health))
                self.attack = round(self.attack + ((value_for_passive / 100) * self.health))
            if self.passive_type == "CRYSTAL":
                self.health = round(self.health - ((value_for_passive / 100) * self.health))
                self.defense = round(self.defense + ((value_for_passive / 100) * self.health))
            if self.passive_type == "FEAR":
                if self.universe != "Chainsawman":
                    self.max_health = self.max_health - (self.max_health * .03)
                player2_card.defense = player2_card.defense - flat_value_for_passive
                player2_card.attack = player2_card.attack - flat_value_for_passive
                player2_card.card_lvl_ap_buff = player2_card.card_lvl_ap_buff - flat_value_for_passive
            if self.passive_type == "GROWTH":
                self.max_health = self.max_health - (self.max_health * .03)
                self.defense = self.defense + flat_value_for_passive
                self.attack = self.attack + flat_value_for_passive
                self.card_lvl_ap_buff = self.card_lvl_ap_buff + flat_value_for_passive
            if self.passive_type == "SLOW":
                if _battle._turn_total != 0:
                   _battle._turn_total = _battle._turn_total - 1
            if self.passive_type == "HASTE":
                _battle._turn_total = _battle._turn_total + 1
            if self.passive_type == "STANCE":
                tempattack = self.attack + flat_value_for_passive
                self.attack = self.defense
                self.defense = tempattack
            if self.passive_type == "CONFUSE":
                tempattack = player2_card.attack - flat_value_for_passive
                player2_card.attack = player2_card.defense
                player2_card.defense = tempattack
            if self.passive_type == "BLINK":
                self.stamina = self.stamina - stam_for_passive
                if player2_card.stamina >=10:
                    player2_card.stamina = player2_card.stamina + stam_for_passive
            if self.passive_type == "BLAST":
                player2_card.health = round(player2_card.health - value_for_passive)
            if self.passive_type == "WAVE":
                if _battle._turn_total % 10 == 0:
                    player2_card.health = round(player2_card.health - 100)


    def activate_chainsawman_trait(self, _battle):
        if self.universe == "Chainsawman":
            if self.health <= (self.max_health * .25):
                if self._chainsawman_activated == True:
                    if self._atk_chainsawman_buff == False:
                        self._atk_chainsawman_buff = True
                        self._chainsawman_activated = False
                        self.defense = self.defense * 2
                        self.attack = self.attack * 2
                        self.max_health = self.max_health * 2
                        _battle.add_battle_history_messsage(f"(**{battle._turn_total}**) **{self.name}** 🩸's Devilization")

            elif self.health <= (self.max_health * .50):
                if self._chainsawman_activated == True:
                    if self._atk_chainsawman_buff == False:
                        self._atk_chainsawman_buff = True
                        self._chainsawman_activated = False
                        self.defense = self.defense * 2
                        self.attack = self.attack * 2
                        self.max_health = self.max_health * 2
                        _battle.add_battle_history_messsage(f"(**{battle._turn_total}**) **{self.name}** 🩸's Devilization")
                        

def get_card(url, cardname, cardtype):
        try:
            # save_path = f"image_cache/{str(cardtype)}/{str(cardname)}.png"
            # # print(save_path)
            
            # if url not in cache:
            #     # print("Not in Cache")
            #     cache[url] = save_path
            #     im = Image.open(requests.get(url, stream=True).raw)
            #     im.save(f"{save_path}", "PNG")
            #     # print(f"NO : {cardname}")
            #     return im

            # else:
            #     # print("In Cache")
            #     im = Image.open(cache[url])
            #     # print(f"YES : {cardname}")
            #     return im
            im = Image.open(requests.get(url, stream=True).raw)
            return im   
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
            


