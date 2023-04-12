import unique_traits as ut
import os
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
        def __init__(self, name, path, price, exclusive, available, is_skin, skin_for, max_health, health, max_stamina, stamina, moveset, attack, defense, type, passive, speed, universe, has_collection, tier, collection, weaknesses, resistances, repels, absorbs, immunity, gif, fpath, rname, rpath, is_boss, card_class):
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
            self.evasion = 0
            self.universe = universe
            self.has_collection = has_collection
            self.tier = tier
            self.collection = collection
            self.weaknesses = weaknesses
            self.resistances = resistances
            self.repels = repels
            self.absorbs = absorbs
            self.immunity = immunity
            self.base_attack  = attack
            self.base_defense = defense
            self.base_health = health
            self.base_max_health = max_health
            self.card_class = card_class
            self.is_fighter = False
            self.is_mage = False
            self.is_ranger = False
            self.is_tank = False
            self.is_healer = False
            self.is_assassin = False
            self.is_swordsman = False
            self.is_summoner = False
            self.is_monstrosity = False

            # Tactics & Classes
            self._swordsman_active = False
            self._swordsman_value = 0
            self._monstrosity_value = 0
            self._critical_strike_count = 0
            self._summoner_active = False
            self._monstrosity_active = False
            self._double_strike_count = 0
            self._magic_active = False
            self._magic_value = 0
            self._heal_active = True
            self._heal_value = 0
            self._heal_buff = .25
            self._assassin_active = False
            self._assassin_value = 0
            self._assassin_attack = 0
            self.tactics = []
            self.max_base_health = self.max_health
            self.temporary_max_health = self.max_health
            self.temporary_health = health
            self.temporary_stamina = stamina
            self.temporary_attack = attack
            self.temporary_defense = defense
            self.temporary_speed = speed
            self.temporary_ap = 0
            self.enraged = False
            self.overwhelming_power = False
            self.damage_check = False
            self.damage_check_activated = False
            self.death_blow = False
            self.almighty_will = False 
            self.stagger = False 
            self.intimidation = False 
            self.loyal_servant = False 
            self.petrified_fear = False
            self.regeneration = False
            self.bloodlust = False


            self.almighty_will_turn = []
            self.damage_check_counter = 0
            self.damage_check_limit = 0
            self.damage_check_turns = 0
            self.petrified_fear_counter = 0
            self.petrified_fear_turns = 0
            self.overwhelming_power_activated = False
            self.overwhelming_power_counter = 0
            self.intimidation_counter = 0
            self.intimidation_turns = 0
            self.intimidation_activated = False
            self.bloodlust_activated = False
            self.enrage_activated = False
            self.regeneration_activated = False
            self.stagger_activated = False
            self.death_blow_activated = False
            self.death_blow_had_protections = False

            # Universe Traits
            self._final_stand = False
            if self.universe == "Dragon Ball Z":
                self._final_stand =True
            self._chainsawman_activated = False
            self._atk_chainsawman_buff = False
            self._def_chainsawman_buff = False
            self._demon_slayer_buff = 0
            self.naruto_heal_buff = 0
            self._gow_resolve = False
            self.temp_opp_arm_shield_active = False
            self.temp_opp_shield_value = 0
            self.temp_opp_arm_barrier_active = False
            self.temp_opp_barrier_value = 0
            self.temp_opp_arm_parry_active = False
            self.temp_opp_parry_value = 0
            self.solo_leveling_trait_swapped = False
            self.solo_leveling_trait_active = False
            self.haki_message = False
            self.breathing_message = False
            self.yuyu_1ap_buff = 0
            self.yuyu_2ap_buff = 0
            self.yuyu_3ap_buff = 0
            self.my_hero_academia_buff_counter = 0
            self.my_hero_academia_buff = 0

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
            self.total_water_buff = 0
            self.gravity_hit = False
            self.physical_meter = 0
            self.barrier_meter = 0
            self.ranged_meter = 0
            self.ranged_hit_bonus = 0
            self.wind_element_activated = False

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
            self.prestige_difficulty = 0

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
            self.usedsummon = False
            self.used_block = False
            self.used_defend = False
            self.used_boost = False
            self.focus_count = 0
            self.damage_recieved = 0
            self.damage_dealt = 0
            self.damage_healed = 0
            self.element_selection = []
            self.move_selection = []
            self.favorite_move = 0
            self.favorite_element = 0
            self.enhance_turn_iterators = 0
            self.stamina_required_to_focus = 10
            self.stamina_focus_recovery_amount = 90
            self._tutorial_message = ""
            self.resolve_value = 60
            self.summon_resolve_message = ""
            self.scheduled_death_message = False
            self.focus_icon = "❤️"
            self.resolve_icon = "🌀"
            self.class_tier = ""
            if self.universe == "Fate":
                self.class_tier = "Elite"
            if self.tier in [4,5]:
                self.class_tier = "Elite"
                if self.universe == "Fate":
                    self.class_tier = "Legendary"
            elif self.tier in [6,7]:
                self.class_tier = "Legendary"
                if self.universe == "Fate":
                    self.class_tier = "Mythical"
            
            self.class_message = f"{self.class_tier} {self.card_class.title()}"
            

            # Talisman Info
            self._talisman = "None"

            # Summon Info
            self.summon_ability_name = ""
            self.summon_power = 0
            self.summon_lvl = 0
            self.summon_type = ""
            self.summon_bond = ""
            self.summon_name = ""
            self.summon_image = ""
            self.summon_universe = ""
            self.summon_bondexp = 0
            self.summon_exp = 0
            self.summon_emoji = ""

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
            self.move1base = self.move1ap
            
            self.move_souls = self.move1
            self.move_souls_ap = self.move1ap
            self.move_souls_stamina = 0
            self.move_souls_element = self.move1_element
            self.move_souls_emoji = self.move1_emoji
            

            # Move 2
            self.move2 = list(self.m2.keys())[0]
            self.move2ap = list(self.m2.values())[0] + self.card_lvl_ap_buff + self.shock_buff + self.special_water_buff + self.arbitrary_ap_buff
            self.move2_stamina = list(self.m2.values())[1]
            self.move2_element = list(self.m2.values())[2]
            self.move2_emoji = crown_utilities.set_emoji(self.move2_element)
            self.move2base = self.move2ap
            

            # Move 3
            self.move3 = list(self.m3.keys())[0]
            self.move3ap = list(self.m3.values())[0] + self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff
            self.move3_stamina = list(self.m3.values())[1]
            self.move3_element = list(self.m3.values())[2]
            self.move3_emoji = crown_utilities.set_emoji(self.move3_element)
            self.move3base = self.move3ap

            # Move Enhancer
            self.move4 = list(self.enhancer.keys())[0]
            self.move4ap = list(self.enhancer.values())[0]
            self.move4_stamina = list(self.enhancer.values())[1]
            self.move4enh = list(self.enhancer.values())[2]
            self.move4base = self.move4ap

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
            self._is_boss = is_boss
            
            # Raid Buffs
            self._raid_defense_buff = 0

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
                value_for_passive = self.tier * .9
                flat_for_passive = round(10 * self.tier)
                stam_for_passive = 5 * (self.tier * .5)
                if self.passive_type == "HLT":
                    self.passive_num = value_for_passive * 2
                if self.passive_type == "LIFE":
                    self.passive_num = value_for_passive
                if self.passive_type == "ATK":
                    self.passive_num = value_for_passive * 2
                if self.passive_type == "DEF":
                    self.passive_num = value_for_passive * 2
                if self.passive_type == "STAM":
                    self.passive_num = stam_for_passive * 2
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
                    self.passive_num = self.passive_num
                if self.passive_type == "HASTE":
                    self.passive_num = self.passive_num
                if self.passive_type == "STANCE":
                    self.passive_num = flat_for_passive * 2
                if self.passive_type == "CONFUSE":
                    self.passive_num = flat_for_passive * 2
                if self.passive_type == "BLINK":
                    self.passive_num = stam_for_passive
                if self.passive_type == "SOULCHAIN":
                    self.passive_num = self.passive_num + 90
                if self.passive_type == "GAMBLE":
                    self.passive_num = self.passive_num

    except:
        print("ERROR")

    def is_universe_unbound(self):
        if(self.universe == "Unbound"):
            return True
        
    def set_passive_num(self, passive_type):
        value_for_passive = self.tier * .5
        flat_for_passive = round(10 * (self.tier * .5))
        stam_for_passive = 5 * (self.tier * .5)
        if passive_type == "HLT":
            self.passive_num = value_for_passive * 2
        if passive_type == "LIFE":
            self.passive_num = value_for_passive
        if passive_type == "ATK":
            self.passive_num = value_for_passive * 2
        if passive_type == "DEF":
            self.passive_num = value_for_passive * 2
        if passive_type == "STAM":
            self.passive_num = stam_for_passive * 2
        if passive_type == "DRAIN":
            self.passive_num = stam_for_passive
        if passive_type == "FLOG":
            self.passive_num = value_for_passive
        if passive_type == "WITHER":
            self.passive_num = value_for_passive
        if passive_type == "RAGE":
            self.passive_num = value_for_passive
        if passive_type == "BRACE":
            self.passive_num = value_for_passive
        if passive_type == "BZRK":
            self.passive_num = value_for_passive
        if passive_type == "CRYSTAL":
            self.passive_num = value_for_passive
        if passive_type == "FEAR":
            self.passive_num = flat_for_passive
        if passive_type == "GROWTH":
            self.passive_num = flat_for_passive
        if passive_type == "CREATION":
            self.passive_num = value_for_passive
        if passive_type == "DESTRUCTION":
            self.passive_num = value_for_passive
        if passive_type == "SLOW":
            self.passive_num = self.passive_num
        if passive_type == "HASTE":
            self.passive_num = self.passive_num
        if passive_type == "STANCE":
            self.passive_num = flat_for_passive
        if passive_type == "CONFUSE":
            self.passive_num = flat_for_passive
        if passive_type == "BLINK":
            self.passive_num = stam_for_passive
        if passive_type == "SOULCHAIN":
            self.passive_num = self.passive_num
        if passive_type == "GAMBLE":
            self.passive_num = self.passive_num

    def set_class_buffs(self):
        value = 0
        p_value = 0
        mage_buff = .35
        heal_buff = .25
        if self.universe == "Fate":
            if self.tier in [1, 2, 3]:
                self.tier = 4
            elif self.tier in [4, 5]:
                self.tier = 6
        if self.tier in [1, 2, 3]:
            value = 1
            p_value = 3
        elif self.tier in [4, 5]:
            value = 2
            p_value = 5
            mage_buff = .45
            heal_buff = .35
        elif self.tier in [6, 7]:
            value = 3
            p_value = 6
            mage_buff = .50
            heal_buff = .45
            if self.universe == "Fate":
                value = 4
                p_value = 8
                mage_buff = .55
                heal_buff = .55
                

        if self.card_class == "FIGHTER":
            self.is_fighter = True
            self._parry_active = True
            self._parry_value = self._parry_value + p_value 
        
        if self.card_class == "MAGE":
            self.is_mage = True
            self._magic_active = True
            self._magic_value = mage_buff
        
        if self.card_class == "RANGER":
            self.is_ranger = True
            self._barrier_active = True
            self._barrier_value = self._barrier_value + value
        
        if self.card_class == "TANK":
            self.is_tank = True
            self._shield_active = True
            if self.universe == "Fate":
                self._shield_value = self._shield_value + (self.tier * 700)
            else:
                self._shield_value = self._shield_value + (self.tier * 500)
        
        if self.card_class == "HEALER":
            self.is_healer = True
            self._heal_active = True
            self._heal_value = 0
            self._heal_buff = heal_buff
        
        if self.card_class == "ASSASSIN":
            self.is_assassin = True
            self._assassin_active = True
            self._assassin_attack = value
            
        if self.card_class == "SWORDSMAN":
            self.is_swordsman = True
            self._swordsman_active = True
            self._swordsman_value = value
            
        if self.card_class == "SUMMONER":
            self.is_summoner = True
            self._summoner_active = True
            
        if self.card_class == "MONSTROSITY":
            self.is_monstrosity = True
            self._monstrosity_active = True
            self._monstrosity_value = value


    # AI ONLY BUFFS
    def set_ai_card_buffs(self, ai_lvl_buff, ai_stat_buff, ai_stat_debuff, ai_health_buff, ai_health_debuff, ai_ap_buff, ai_ap_debuff, prestige_level, rebirth_level, mode):
        self.set_class_buffs()

        if rebirth_level > 0 or prestige_level > 0: 
            self.prestige_difficulty = ((((prestige_level + 1) * (10 + rebirth_level)) /100)) 
        else:
            self.prestige_difficulty = 0   
        # print(self.prestige_difficulty)
        if mode == "Abyss" or mode == "SCENARIO" or mode == "RAID" or mode == "EXPLORE":
            self.card_lvl = ai_lvl_buff
        else:
            self.card_lvl = self.get_ai_card_level(ai_lvl_buff, mode)
        # print(self.card_lvl)
        # print(self.move1ap)
        self.card_lvl_ap_buff = crown_utilities.level_sync_stats(self.card_lvl, "AP")
        self.card_lvl_attack_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_defense_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_hlt_buff = crown_utilities.level_sync_stats(self.card_lvl, "HLT")
        
        # print(self.card_lvl_ap_buff)
        self.max_health = round(self.max_health + self.card_lvl_hlt_buff + ai_health_buff + ai_health_debuff + ((self.card_lvl_hlt_buff  + ai_ap_buff + ai_ap_debuff) * self.prestige_difficulty ))
        self.health = round(self.health + self.card_lvl_hlt_buff + ai_health_buff + ai_health_debuff + ((self.card_lvl_hlt_buff  + ai_ap_buff + ai_ap_debuff) * self.prestige_difficulty ))
        self.attack = round(self.attack + self.card_lvl_attack_buff + ai_stat_buff + ai_stat_debuff + ((self.card_lvl_attack_buff  + ai_ap_buff + ai_ap_debuff) * self.prestige_difficulty ))
        self.defense = round(self.defense + self.card_lvl_defense_buff + ai_stat_buff + ai_stat_debuff + ((self.card_lvl_defense_buff  + ai_ap_buff + ai_ap_debuff) * self.prestige_difficulty ))
        self.move1ap = round(self.move1ap + self.card_lvl_ap_buff + ai_ap_buff + ai_ap_debuff + ((self.card_lvl_ap_buff + ai_ap_buff + ai_ap_debuff) * self.prestige_difficulty ))
        self.move2ap = round(self.move2ap + self.card_lvl_ap_buff + ai_ap_buff + ai_ap_debuff + ((self.card_lvl_ap_buff + ai_ap_buff + ai_ap_debuff) * self.prestige_difficulty ))
        self.move3ap = round(self.move3ap + self.card_lvl_ap_buff + ai_ap_buff + ai_ap_debuff + ((self.card_lvl_ap_buff + ai_ap_buff + ai_ap_debuff) * self.prestige_difficulty ))
        # print(self.move1ap)

    def get_ai_card_level(self, card_lvl, mode):
        # print(mode)
        if mode == "Tales":
            if card_lvl >= 210:
                return 200
            elif card_lvl >= 10:
                if card_lvl <= 20 and card_lvl >=10:
                    return 10
                elif card_lvl >= 0 and card_lvl <=10:
                    return card_lvl
                else:
                    return (card_lvl - 10)
            else:
                return card_lvl
        elif mode == "Dungeon":
            if card_lvl >= 600:
                return 650
            else:
                if card_lvl <= 350:
                    return 350
                elif card_lvl <= 500:
                    if card_lvl <= 590 and card_lvl >=550:
                        return card_lvl + 20
                    else:
                        return card_lvl + 30
                else:
                    return card_lvl + 50
        elif mode == "DTales":
            if card_lvl < 400:
                return 400
            else:
                return card_lvl
        elif mode == "DDungeon":
            if card_lvl >= 600:
                return 650
            else:
                if card_lvl <= 400:
                    return 400
                else:
                    return card_lvl + 50
        elif mode == "CTales":
            if card_lvl >= 285:
                return 300
            else:
                return card_lvl + 15
        elif mode == "CDungeon":
            if card_lvl >= 600:
                return 550
            else:
                if card_lvl <= 400:
                    return 400
                else:
                    return card_lvl + 50
        elif mode == "Boss":
            return 1000
        elif mode == "CBoss":
            return 1000
    
    
    def set_raid_defense_buff(self, hall_defense):
        self.defense = round(self.defense * hall_defense)
        
    
    # This method will set the level buffs & apply them
    def set_card_level_buffs(self, list_of_card_levels=None):
        try:
            self.set_class_buffs()

            if list_of_card_levels:
                for x in list_of_card_levels:
                    if x.get('CARD') == self.name:
                        self.card_lvl = x.get('LVL', 0)
                        self.card_exp = x.get('EXP', 0)
                        break

            self.card_lvl_ap_buff = crown_utilities.level_sync_stats(self.card_lvl, "AP")
            self.card_lvl_attack_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
            self.card_lvl_defense_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
            self.card_lvl_hlt_buff = crown_utilities.level_sync_stats(self.card_lvl, "HLT")

            self.max_health = self.max_health + self.card_lvl_hlt_buff
            self.health = self.health + self.card_lvl_hlt_buff
            self.attack = self.attack + self.card_lvl_attack_buff
            self.defense = self.defense + self.card_lvl_defense_buff
            self.move1ap = self.move1ap + self.card_lvl_ap_buff
            self.move2ap = self.move2ap + self.card_lvl_ap_buff
            self.move3ap = self.move3ap + self.card_lvl_ap_buff

            if self.summon_type in ['BARRIER', 'PARRY']:
                if self.summon_bond == 3 and self.summon_lvl == 10:
                    self.summon_power = self.summon_power + 1
            else:
                self.summon_power = (self.summon_bond * self.summon_lvl) + self.summon_power
        except:
            # print("Error setting card levels")
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
        elif self.exclusive == True and self.available == False and self.has_collection == False:
            self.price_message = "Scenario Only"
            self.card_icon = f"🎞️"
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
                self.move1ap = self.move1ap + arm_value + self.card_lvl_ap_buff
                self.move1base = self.move1ap
                self.move1_element = arm_element
                self.move1_emoji = crown_utilities.set_emoji(self.move1_element)
                

            if arm_type == "SPECIAL":
                self.move2 = arm_name
                self.move2ap = self.move2ap + arm_value + self.card_lvl_ap_buff
                self.move2base = self.move2ap
                self.move2_element = arm_element
                self.move2_emoji = crown_utilities.set_emoji(self.move2_element)


            if arm_type == "ULTIMATE":
                self.move3 = arm_name
                self.move3ap = self.move3ap + arm_value + self.card_lvl_ap_buff
                self.move3base = self.move3ap
                self.move3_element = arm_element
                self.move3_emoji = crown_utilities.set_emoji(self.move3_element)

            if arm_type == "ULTIMAX":
                self.move1ap = self.move1ap + arm_value
                self.move2ap = self.move2ap + arm_value
                self.move3ap = self.move3ap + arm_value
                self.move1base = self.move1ap
                self.move2base = self.move2ap
                self.move3base = self.move3ap

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
                self.move4ap = round(self.move4ap + (self.move4ap * (arm_value / 100)))

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
        licon = "🔰"
        if self.card_lvl >= 200:
            licon ="🔱"
        if self.card_lvl >= 700:
            licon ="⚜️"
        if self.card_lvl > 999:
            licon ="🏅"
        
        return licon


    # Explore Methods    
    def set_explore_bounty_and_difficulty(self, battle_config):
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
            self.card_lvl = random.randint(500, 999)
            self.bounty = self.bounty * 15


        if mode_selector_randomizer <= 19:
            selected_mode = "Impossible"
            self.approach_message = "👹 An Impossible "
            self._explore_cardtitle = {'TITLE': 'Dungeon Title'}
            self.card_lvl = random.randint(850, 1500)
            self.bounty = self.bounty * 150

        if self.tier == 7:
            self.card_lvl = random.randint(1000, 1800)
        if self.tier == 6:
            self.card_lvl = random.randint(900, 1500)


        if battle_config.is_hard_difficulty:
            self.attack = self.attack + 1000 + (200 *self.tier)
            self.defense = self.defense + 1000 + (200 * self.tier)
            self.max_health = self.max_health + (1000 * self.tier)
            self.health = self.health + (1000 * self.tier)
            random_mod = random.randint(0,1500000)
            self.bounty = self.bounty + (2000000 * self.tier) + random_mod

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
        self.battle_message = f"\n:crown: | **Glory**: Earn {self.name} & 2x Bounty, If you Lose, You lose gold!\n:coin: | **Gold**: Earn gold only!"

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
            
        if self.summon_type == "WATER":
            self.basic_water_buff = self.basic_water_buff + num
        


    def set_bleed_hit(self, turn_total, opponent_card):
        if opponent_card.bleed_hit:
            opponent_card.bleed_hit = False
            bleed_hit_local = 10 * turn_total
            bleed_hit_modified = bleed_hit_local + (self.health * .05)
            self.health = self.health - bleed_hit_modified
            if self.health < 0:
                self.health = -999
            self.damage_recieved = self.damage_recieved + round(bleed_hit_modified)
            opponent_card.damage_dealt = opponent_card.damage_dealt + round(bleed_hit_modified)
            return f"🩸 **{self.name}** shredded for **{round(bleed_hit_modified)}** bleed dmg..."


    def set_burn_hit(self, opponent_card):
        # print(opponent_card.name)
        # print(opponent_card.burn_dmg)
        burn_message = None
        if opponent_card.burn_dmg > 15:
            self.health = self.health - opponent_card.burn_dmg
            burn_message =  f"🔥 **{self.name}** burned for **{round(opponent_card.burn_dmg)}** dmg..."
            self.damage_recieved = self.damage_recieved + round(opponent_card.burn_dmg)
            opponent_card.damage_dealt = opponent_card.damage_dealt + round(opponent_card.burn_dmg)
            if self.health <= 0:
                self.health = -999
                burn_message = f"🔥 **{self.name}** burned for **{round(opponent_card.burn_dmg)}** dmg and died..."
                opponent_card.burn_dmg = 0
        
        opponent_card.burn_dmg = opponent_card.burn_dmg / 2
        if opponent_card.burn_dmg <= 14 and self.health > 0:
            opponent_card.burn_dmg = 0
            burn_message = None
        
        return burn_message


    def frozen(self, battle_config, opponent_card):
        if opponent_card.freeze_enh:
            battle_config.turn_total = battle_config.turn_total + 1
            battle_config.next_turn()


        return {"MESSAGE" : f"❄️ **{self.name}** has been frozen for a turn...", "TURN": battle_config.is_turn}



    def activate_demon_slayer_trait(self, battle_config, opponent_card):
        if self.universe == "Demon Slayer" and not self.breathing_message:
            battle_config.turn_zero_has_happened = True
            self.breathing_message = True
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Total Concentration Breathing: **Increased HP by {round(opponent_card.health * .40)}**")
            self.health = round(self.health + (opponent_card.health * .40))
            self.max_health = round(self.max_health + (opponent_card.health *.40))
            
    def activate_observation_haki_trait(self, battle_config, opponent_card):
        if self.universe == "One Piece" and not self.haki_message:
            battle_config.turn_zero_has_happened = True
            self.haki_message = True
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Observation Haki: **40% Damage Reduction Until First Focus!**")

    

    def set_poison_hit(self, opponent_card):
        if opponent_card.poison_dmg:
            self.health = self.health - opponent_card.poison_dmg
            if self.health <  0:
                self.health = 0
            self.damage_recieved = self.damage_recieved + round(opponent_card.poison_dmg)
            opponent_card.damage_dealt = opponent_card.damage_dealt + round(opponent_card.poison_dmg)
            return f"🧪 **{self.name}** poisoned for **{opponent_card.poison_dmg}** dmg..."


    def set_gravity_hit(self):
        if self.gravity_hit:
            self.gravity_hit = False


    def set_solo_leveling_config(self, opponent_shield_active, opponent_shield_value, opponent_barrier_active, opponent_barrier_value, opponent_parry_active, opponent_parry_value):
        if self.universe == "Solo Leveling":
            self.solo_leveling_trait_active = True 
            if opponent_shield_active and self.temp_opp_shield_value <= 0:
                self.temp_opp_arm_shield_active = True
                self.temp_opp_shield_value += opponent_shield_value
            
            if opponent_barrier_active and self.temp_opp_barrier_value <= 0:
                self.temp_opp_arm_barrier_active = True
                self.temp_opp_barrier_value += opponent_barrier_value
            
            if opponent_parry_active and self.temp_opp_parry_value <= 0:
                self.temp_opp_arm_parry_active = True
                self.temp_opp_parry_value += opponent_parry_value


    def add_solo_leveling_temp_values(self, protection, opponent_card):
        if opponent_card.universe == "Solo Leveling":
            if protection == "BARRIER":
                opponent_card.temp_opp_arm_barrier_active = True
                opponent_card.temp_opp_barrier_value += self._barrier_value

            if protection == "SHIELD":
                opponent_card.temp_opp_arm_shield_active = True
                opponent_card.temp_opp_shield_value += self._shield_value
            
            if protection == "PARRY":
                opponent_card.temp_opp_arm_parry_active = True
                opponent_card.temp_opp_parry_value += self._parry_value

    def decrease_solo_leveling_temp_values(self, protection, opponent_card, battle_config):
        if opponent_card.universe == "Solo Leveling":
            if protection == "BARRIER":
                opponent_card._barrier_active = True
                opponent_card._barrier_value = opponent_card.temp_opp_barrier_value
                opponent_card.temp_opp_arm_barrier_active = False
                opponent_card.temp_opp_barrier_value = 0

            if protection == "SHIELD":
                opponent_card._shield_active = True
                opponent_card._shield_value = opponent_card.temp_opp_shield_value
                opponent_card.temp_opp_arm_shield_active = False
                opponent_card.temp_opp_shield_value = 0
            
            if protection == "PARRY":
                opponent_card._parry_active = True
                opponent_card._parry_value = opponent_card.temp_opp_parry_value
                opponent_card.temp_opp_arm_parry_active = True
                opponent_card.temp_opp_parry_value = 0

            battle_config.add_to_battle_log(f"🩸 **ARISE!** *{opponent_card.name}* has gained your lost protections...")

    def decrease_solo_leveling_temp_values_self(self, protection, battle_config):
        if self.universe == "Solo Leveling":
            if protection == "BARRIER":
                self._barrier_active = True
                self._barrier_value = self.temp_opp_barrier_value
                self.temp_opp_arm_barrier_active = False
                self.temp_opp_barrier_value = 0

            if protection == "SHIELD":
                self._shield_active = True
                self._shield_value = self.temp_opp_shield_value
                self.temp_opp_arm_shield_active = False
                self.temp_opp_shield_value = 0
            
            if protection == "PARRY":
                self._parry_active = True
                self._parry_value = self.temp_opp_parry_value
                self.temp_opp_arm_parry_active = True
                self.temp_opp_parry_value = 0

            battle_config.add_to_battle_log(f"🩸 **ARISE!** *{self.name}* has gained your lost protections...")



    def activate_solo_leveling_trait(self, battle_config, opponent_card):
        # Make sure that if opponent shield, barrier, or parry breaks you gain that temp value
        if self.universe == "Solo Leveling":
            if opponent_card.temp_opp_arm_shield_active and not opponent_card._shield_active:
                if self._shield_active:
                    self._shield_value = self._shield_value + opponent_card._shield_value
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
                elif not self._shield_active:
                    self._shield_active = True
                    self._shield_value = opponent_card.temp_opp_shield_value
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
            
            elif opponent_card.temp_opp_arm_parry_active and not opponent_card._barrier_active:
                if self._barrier_active:
                    self._barrier_value = self._barrier_value + opponent_card.temp_opp_barrier_value
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
                elif not self._barrier_active:
                    self._barrier_active = True
                    self._barrier_value = opponent_card.temp_opp_barrier_value
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
            
            elif opponent_card.temp_opp_arm_parry_active and not opponent_card._parry_value:
                if self._parry_active:
                    self._parry_value = self._parry_value + opponent_card.temp_opp_parry_value
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True
                elif not self._parry_active:
                    self._parry_active = True
                    self._parry_value = opponent_card.temp_opp_parry_value
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 **ARISE!** *{opponent_card.name}* is now yours")
                    self.solo_leveling_trait_swapped = True


    def set_deathnote_message(self, battle_config):
        if not self.scheduled_death_message:
            if self.universe == "Death Note":
                self.scheduled_death_message = True
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Scheduled Death 📓 **Turn {130 + (10 * self.tier)}**")


    def set_souls_trait(self):
        if self.used_resolve and self.universe == "Souls":
            self.move_souls = self.move1
            self.move_souls_ap = self.move1ap
            self.move_souls_stamina = 0
            self.move_souls_element = self.move1_element
            self.move_souls_emoji = self.move1_emoji
            
            self.move1 = self.move2
            self.move1ap = self.move2ap
            self.move1_stamina = self.move1_stamina
            self.move1_element = self.move2_element
            self.move1_emoji = self.move2_emoji
            
            self.move2 = self.move3
            self.move2ap = self.move3ap
            self.move2_stamina = self.move2_stamina
            self.move2_element = self.move3_element
            self.move2_emoji = self.move3_emoji


    def get_card_index(self, list_of_cards):
        try:
            self.index = list_of_cards.index(self.name)
            return self.index
        except:
            return 0
        

    def get_evasion(self):
        if self.speed <=30:
            self.evasion = -1 * (crown_utilities.calculate_speed_modifier(self.speed) * 5)
        elif self.speed >=70:
            self.evasion = -1 * (crown_utilities.calculate_speed_modifier(self.speed) * 5)


    def activate_my_hero_academia_trait(self):
        if self.universe == "My Hero Academia" and not self.used_resolve:
            self.my_hero_academia_buff_counter += 10
        
        if self.universe == "My Hero Academia" and self.used_resolve and self.my_hero_academia_buff > 50:
            self.my_hero_academia_buff -= 50


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
                    title_passive_msg = title.passive_value
                    # if title.passive_type == "SOULCHAIN":
                    #     title_passive_msg = title.passive_value + 90 
                    title_message = f"{title.passive_type.title()} {title_passive_msg}"
                    title_len = int(len(list(title.name)))

                self.set_passive_num(self.passive_num)
                card_message = f"{self.passive_type.title()} {self.passive_num}"
                
                #Evasion
                evasion = self.get_evasion()
                evasion_message = f"{self.speed}"
                if self.speed >= 70 or self.speed <=30:
                    evasion_message = f"{self.speed} *{self.evasion}%*"
                    
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
                    # self.d_emoji_1 = ebasic
                    # self.d_emoji_2 = especial
                    # self.d_emoji_3 = eultimate
                    


                if arm != "none":
                    arm_message = f"{arm.passive_type.title()} | {arm.passive_value}"
                    if arm.passive_type in crown_utilities.ABILITY_ARMS:
                        arm_element_icon = crown_utilities.set_emoji(arm.element)
                        arm_message = f"{arm_element_icon} {arm.passive_type.title()}"
                        #self.element = arm.element
                 
                
                        
                        
                    

                if mode == "non-battle":
                    ebasic = ""
                    especial = ""
                    eultimate = ""

                if len(self.move1) > 40:
                    self.move1 = self.move1[:37] + "..."
                if len(self.move2) > 40:
                    self.move2 = self.move2[:37] + "..."
                if len(self.move3) > 40:
                    self.move3 = self.move3[:37] + "..."
                move1_text = f"{self.move1_emoji} {self.move1}: {self.move1ap} {ebasic}"
                move2_text = f"{self.move2_emoji} {self.move2}: {self.move2ap} {especial}"
                move3_text = f"{self.move3_emoji} {self.move3}: {self.move3ap} {eultimate}"
                

                turn_crit = False
                if self.move4enh in crown_utilities.Turn_Enhancer_Check:
                    if turn_total in [0,1] :
                        self.move4ap = round(self.move4base)
                        turn_crit = True
                    elif turn_total % 10 == 0:
                        self.move4ap = round(self.move4base)
                        turn_crit = True
                    elif turn_total >= 1:
                        self.move4ap = round(self.move4base / turn_total)

                elif self.move4enh in crown_utilities.Damage_Enhancer_Check:
                    if turn_total > 0:
                        self.move4ap = round(self.move4base * turn_total)
                        if self.move4ap >= (100 * self.tier):
                            if self.move4enh == "BLAST":
                                self.move4ap = (100 * self.tier)
                            else:
                                self.move4ap = (100 * self.tier)
                            turn_crit = True
                
                # move4enh is the TYPE of enhancer
                if not turn_crit:
                    move_enhanced_text = f"🦠 {self.move4}: {self.move4enh} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"
                elif self.move4enh in crown_utilities.Damage_Enhancer_Check and self.move4ap == (100 * self.tier):
                    move_enhanced_text = f"🎇 {self.move4}: {self.move4enh} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"
                elif self.move4enh in crown_utilities.Turn_Enhancer_Check and (turn_total % 10 == 0 or turn_total in [0,1]):
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
                if int(self.card_lvl) > 999:
                    lvl_sizing = (45, 70)
                draw.text(lvl_sizing, f"{self.card_lvl}", (255, 255, 255), font=lvl_font, stroke_width=1, stroke_fill=(0, 0, 0),
                        align="center")

                # Health & Stamina
                rift_universes = ['Crown Rift Awakening']
                if self.universe in rift_universes or self.is_skin:
                    draw.text((730, 417), health_bar, (0, 0, 0), font=health_and_stamina_font, align="left")
                    draw.text((730, 457), f"{round(self.stamina)}", (0, 0, 0), font=health_and_stamina_font, align="left")
                else:
                    draw.text((730, 417), health_bar, (255, 255, 255), font=health_and_stamina_font, stroke_width=1,
                            stroke_fill=(0, 0, 0), align="left")
                    draw.text((730, 457), f"{round(self.stamina)}", (255, 255, 255), font=health_and_stamina_font, stroke_width=1,
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
                    title_message_on_card = f"🎗️None 🦾None"
                else:
                    title_suffix = crown_utilities.title_enhancer_suffix_mapping[title.passive_type]
                    if mode == "battle":
                        title_message_on_card = f"🎗️{title_message}{title_suffix}"
                    else:
                        title_message_on_card = f"🎗️{title_message}{title_suffix}  🦾{arm_message}"


                card_suffix = crown_utilities.passive_enhancer_suffix_mapping[self.passive_type]

                with Pilmoji(im) as pilmoji:
                    # pilmoji.text((945, 445), crown_utilities.class_emojis[self.card_class], (0, 0, 0), font=health_and_stamina_font, align="left")
                    pilmoji.text((602, 138), f"{title_message_on_card}", (255, 255, 255), font=title_font, stroke_width=1, stroke_fill=(0, 0, 0),
                        align="left")
                    pilmoji.text((602, 180), f"🩸{card_message}{card_suffix}  🏃{self.speed}", (255, 255, 255), font=passive_font, stroke_width=1, stroke_fill=(0, 0, 0),
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
    

    def damage_cal(self, selected_move, battle_config, _opponent_card):
        if self.defense <= 0:
            self.defense = 25
        if self.attack <= 0:
            self.attack = 25
        if _opponent_card.defense <= 0:
            _opponent_card.defense = 25
        if _opponent_card.attack <= 0:
            _opponent_card.attack = 25

        enhancer = False
        can_use_move_flag = True
        move_element = ""
        summon_used = False

        ENHANCERS = [4]
        MOVES = [1,2,3,6]
        
        if selected_move == "Souls":
            does_repel = False
            does_absorb = False
            self.wind_element_activated = False
            is_physical_element = False
            ranged_attack = False
            wind_buff = 0

            move = self.move_souls
            ap = self.move_souls_ap
            move_stamina = 0
            move_element = self.move_souls_element
            
            if move_element == "WIND":
                self.wind_element_activated = True
            if move_element == "RANGED" and move_stamina >= 30:
                ranged_attack = True
            if move_element == "PHYSICAL" and move_stamina >= 80:
                is_physical_element = True
            move_emoji = crown_utilities.set_emoji(move_element)

        elif selected_move in MOVES:
            does_repel = False
            does_absorb = False
            self.wind_element_activated = False
            is_physical_element = False
            ranged_attack = False
            wind_buff = 0

            if selected_move == 1:
                move = self.move1
                ap = self.move1ap
                move_stamina = self.move1_stamina
                move_element = self.move1_element

            if selected_move == 2:
                move = self.move2
                ap = self.move2ap
                move_stamina = self.move2_stamina
                move_element = self.move2_element

            if selected_move == 3:
                move = self.move3
                ap = self.move3ap
                move_stamina = self.move3_stamina
                move_element = self.move3_element

            if move_element == "WIND":
                self.wind_element_activated = True
            if move_element == "RANGED" and move_stamina >= 30:
                ranged_attack = True
            if move_element == "PHYSICAL" and move_stamina >= 80:
                is_physical_element = True
            move_emoji = crown_utilities.set_emoji(move_element)

            if selected_move == 6:
                move_element = self.summon_type
                # move_emoji = self.summon_emoji
                move_emoji = crown_utilities.set_emoji(move_element)
                can_use_move_flag = True
                ap = self.summon_power
                move_stamina = 0
                move = self.summon_ability_name
                summon_used = True
                protections = ['BARRIER', 'SHIELD', 'PARRY']
                if move_element in protections:
                    if move_element == "BARRIER":
                        self._barrier_active = True
                        if self._barrier_value < 0:
                            self._barrier_value = 0
                        self._barrier_value = self._barrier_value + ap
                        self.add_solo_leveling_temp_values('BARRIER', _opponent_card)
                        message = f"🧬 {self.name} summoned **{self.summon_name}**\n💠 {move} was used! {self.name} received {self.summon_emoji} {ap} barrier"
                    if move_element == "SHIELD":
                        self._shield_active = True
                        if self._shield_value < 0:
                            self._shield_value = 0
                        self._shield_value = self._shield_value + ap
                        self.add_solo_leveling_temp_values('SHIELD', _opponent_card)
                        message = f"🧬 {self.name} summoned **{self.summon_name}**\n🌐 {move} was used! {self.name} received {self.summon_emoji} {ap} shield!"
                    if move_element == "PARRY":
                        self._parry_active = True
                        if self._parry_value < 0:
                            self._parry_value = 0
                        self._parry_value = self._parry_value + ap
                        self.add_solo_leveling_temp_values('PARRY', _opponent_card)
                        message = f"🧬 {self.name} summoned **{self.summon_name}**\n🔄 {move} was used! {self.name} receive {self.summon_emoji} {ap} parry!"
                    # battle_config.add_to_battle_log(message)
                    response = {
                    "DMG": 0,
                    "MESSAGE": message,
                    "CAN_USE_MOVE": can_use_move_flag,
                    "ENHANCE": False,
                    "REPEL": False,
                    "ABSORB": False,
                    "ELEMENT": move_element,
                    "SUMMON_USED" : True
                    }
                    return response            

        if selected_move in ENHANCERS:
            enhancer = True
            enh = self.move4enh
            ap = self.move4ap
            move_stamina = self.move4_stamina
            move = self.move4

        if (self.stamina - move_stamina) < 0:
            print("Not enough stamina to use this move!")   
            if not summon_used:
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

        if enhancer:
            tier = self.tier
            attack = self.attack
            defense = self.defense
            stamina = self.stamina
            health = self.health
            max_health = self.max_health

            enhancement_types = {
                "ATK": lambda ap: round((ap / 100) * attack),
                "DEF": lambda ap: round((ap / 100) * defense),
                "STAM": lambda ap: ap,
                "HLT": lambda ap: 0 if health == max_health else round(100 + min(ap, max_health - health) + (.15 * health) + (.20 * (max_health - health))),
                "LIFE": lambda ap: 0 if health >= max_health else round(min(ap, max_health - health) + (.10 * _opponent_card.health) + (.10 * (self.max_health - self.health)) if (ap + self.health) <= max_health else (max_health - health) + (.10 * _opponent_card.health) + (.10 * (self.max_health - self.health))),
                "DRAIN": lambda ap: round(ap),
                "FLOG": lambda ap: round((ap / 100) * min(_opponent_card.attack, 2000)),
                "WITHER": lambda ap: round((ap / 100) * min(_opponent_card.defense, 2000)),
                "RAGE": lambda ap: round((ap / 100) * min(defense, 2000)),
                "BRACE": lambda ap: round((ap / 100) * min(attack, 2000)),
                "BZRK": lambda ap: round((ap / 100) * health),
                "CRYSTAL": lambda ap: round((ap / 100) * health),
                "GROWTH": lambda ap: round(ap),
                "STANCE": lambda ap: attack + ap,
                "CONFUSE": lambda ap: _opponent_card.attack - ap,
                "BLINK": lambda ap: ap,
                "SLOW": lambda ap: ap,
                "HASTE": lambda ap: ap,
                "FEAR": lambda ap: ap,
                "SOULCHAIN": lambda ap: ap,
                "GAMBLE": lambda ap: ap,
                "WAVE": lambda ap: ap if battle_config.is_turn == 0 else (ap if battle_config.turn_total % 10 == 0 else ap / battle_config.turn_total),
                "BLAST": lambda ap: ap if battle_config.turn_total == 0 else min(round(ap * battle_config.turn_total), 100 * self.tier),
                "CREATION": lambda ap: ap if battle_config.is_turn == 0 else (ap if battle_config.turn_total % 10 == 0 else (ap * 2 if battle_config.turn_total == round(random.randint(2, 50)) else ap / battle_config.turn_total)),
                "DESTRUCTION": lambda ap: ap if battle_config.turn_total == 0 else min(round(ap * battle_config.turn_total), 100 * self.tier), 
            }


            enhancer_value = enhancement_types.get(enh, lambda ap: 0)(ap)
            
            def get_message(move, enh, enhancer_value, tier):
                    legend = {
                        "ATK": "Attack",
                        "DEF": "Defense",
                        "STAM": "Stamina",
                        "HLT": "Health",
                        "LIFE": "Health",
                        "DRAIN": "Stamina",
                        "FLOG": "Attack",
                        "WITHER": "Defense",
                        "RAGE": "Defense",
                        "BRACE": "Attack",
                        "BZRK": "Health",
                        "CRYSTAL": "Health",
                        "RAGE_INC": "AP",
                        "BRACE_INC": "AP",
                        "BZRK_INC": "Attack",
                        "CRYSTAL_INC": "Defense",
                        "WAVE": "Wave",
                        "BLAST": "Blast"
                    }
                    if enh in ['ATK', 'DEF', 'STAM']:
                        message = f"{move} used! Increasing {legend[enh]} by {enhancer_value}"
                    elif enh in ['LIFE', 'DRAIN', 'FLOG', 'WITHER']:
                        if enh == 'LIFE' and enhancer_value == 0:
                            message = f"{move} used! Stealing {enhancer_value} Health... Your Health is full!"
                        else:
                            if enh == "LIFE":
                                if enhancer_value + self.health >= self.max_health:
                                    enhancer_value = round(self.max_health - self.health)
                            message = f"{move} used! Stealing {enhancer_value} {legend[enh]}!"
                    elif enh in ['RAGE', 'BRACE', 'BZRK', 'CRYSTAL']:
                        message = f"{move} used! Sacrificing {enhancer_value} {legend[enh]}, Increasing {legend[f'{enh}_INC']} by {enhancer_value}"
                    elif enh in ['WAVE', 'BLAST']:
                        if enh == 'BLAST' and enhancer_value > (100 * self.tier):
                            enhancer_value = (100 * self.tier)
                        message = f"{move} used! Dealing {round(enhancer_value)} {legend[enh]} Damage!"
                    elif enh in ['CREATION', 'DESTRUCTION']:
                        if enh == 'DESTRUCTION' and enhancer_value > (100 * self.tier):
                            enhancer_value = (100 * self.tier)
                        message = f"{move} used! {'Healing' if enh == 'CREATION' else 'Destroying'} {round(enhancer_value)} {'Max Health' if enh == 'DESTRUCTION' else 'Health and Max Health'}"
                    elif enh == 'GROWTH':
                        message = f"{move} used! Sacrificing 10% Max Health to Increase Attack, Defense and AP by {round(enhancer_value)}"
                    elif enh in ['STANCE', 'CONFUSE']:
                        message = f"{move} used! Swapping {'Opponent Attack and Defense' if enh == 'CONFUSE' else 'Attack and Defense'}, {'Decreasing Defense' if enh == 'CONFUSE' else 'Increasing Defense'} to {enhancer_value}"
                    elif enh in ['HLT', 'FEAR']:
                        if enh == 'HLT' and enhancer_value == 0:
                            message = f"{move} used! Healing for {enhancer_value} Health... Your Health is full!"
                        else:
                            if enhancer_value + self.health >= self.max_health:
                                enhancer_value = self.max_health - self.health
                            message = f"{move} used! {'Healing' if enh == 'HLT' else 'Sacrificing 10% Max Health to Decrease Opponent Attack, Defense and AP'} by {round(enhancer_value)}"
                    elif enh in ['SOULCHAIN', 'GAMBLE']:
                        message = f"{move} used! Synchronizing {'Stamina' if enh == 'SOULCHAIN' else 'Health'}  to {enhancer_value}"
                    else:
                        message = f"{move} used! Inflicts {enh}"
                    return message
            
            m = get_message(move, enh, enhancer_value, self.tier)
            if move_stamina != 15:
                self.stamina = self.stamina - move_stamina

            if _opponent_card.damage_check_activated:
                damage_check_message = f"**[[Damage Check] {round(_opponent_card.damage_check_counter)} damage done so far]**"
                battle_config.add_to_battle_log(damage_check_message)
                _opponent_card.damage_check_turns = _opponent_card.damage_check_turns - 1
                if _opponent_card.damage_check_counter >= _opponent_card.damage_check_limit:
                    damage_check_message = f"✅ **[{self.name} passed the Damage Check]**"
                    battle_config.add_to_battle_log(damage_check_message)
                    _opponent_card.damage_check_activated = False
                    _opponent_card.damage_check_counter = 0
                    _opponent_card.damage_check_limit = 0
                    _opponent_card.damage_check_turns = 0
                    _opponent_card.damage_check = False
                elif _opponent_card.damage_check_turns <= 0:
                    _opponent_card.damage_check_activated = False
                    _opponent_card.damage_check_counter = 0
                    _opponent_card.damage_check_limit = 0
                    _opponent_card.damage_check_turns = 0
                    _opponent_card.damage_check = False
                    self.health = 0
                    self.defense = 0
                    self.attack = 0
                    damage_check_message = f"❌ **[{self.name} failed the Damage Check]**"
                battle_config.add_to_battle_log(damage_check_message)
            
            response = {"DMG": enhancer_value, "MESSAGE": m,
                        "CAN_USE_MOVE": can_use_move_flag, "ENHANCED_TYPE": enh, "ENHANCE": True, "STAMINA_USED": move_stamina, "SUMMON_USED": False}
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
                    if dmg > (ap * 1.2): 
                        dmg = ap * 1.2
                elif dmg < (ap / 2):  
                    if _opponent_card.defense >= (self.attack * 2):
                        dmg = ap / 3
                    else:
                        dmg = ap / 2
                
                low = dmg - (dmg * .20)
                high = dmg + (dmg * .05)
                true_dmg = (round(random.randint(int(low), int(high)))) + 25

                message = ""            

                miss_hit = 1
                low_hit = 6
                med_hit = 15
                standard_hit = 19
                high_hit = 20
                # hit_roll = round(random.randint(0, 20))
                hit_roll = round(random.randint(1, 20))  # generate a random integer between 1 and 20 inclusive
                evasion = crown_utilities.calculate_speed_modifier(_opponent_card.speed)
                speed_mod = self.speed / 10
                if speed_mod < 1:
                    speed_mod = speed_mod * 10
                opponent_speed_mod = _opponent_card.speed / 10
                if opponent_speed_mod < 1:
                    opponent_speed_mod = opponent_speed_mod * 10
                accuracy = speed_mod - opponent_speed_mod
                if accuracy <= 0:
                    accuracy = 0
                if accuracy >= 3:
                    accuracy = 3
                hit_roll += evasion + accuracy
                spirit_crit = False
                #Evasion Modifier
                hit_roll = self.adjust_hit_roll(hit_roll, _opponent_card, summon_used, true_dmg, move_element, battle_config, low_hit, med_hit, standard_hit, high_hit, miss_hit)

                if move_element == "RECOIL" and hit_roll > miss_hit:
                    true_dmg = round(true_dmg * (1 + accuracy))

                if self.wind_element_activated and hit_roll < miss_hit:
                    battle_config._wind_buff = round(battle_config._wind_buff + round(true_dmg * .25))
                    battle_config.add_to_battle_log(f"*The wind is mustering... all wind power increased by {round(true_dmg * .25)}*")
                    true_dmg = round(true_dmg + battle_config._wind_buff)

                if move_element == "SPIRIT" and hit_roll >= 20:
                    spirit_crit = True
                if hit_roll < miss_hit:
                    if self.universe == 'Crown Rift Slayers':
                        true_dmg = round(true_dmg * 2.5)
                        message = f'🩸{move_emoji} Feint Attack! {move} Critically Hits {_opponent_card.name} for {true_dmg}!! 💥 '
                    elif self.wind_element_activated:
                        true_dmg = round(true_dmg)
                        message = f'🌪️ Wind Attack! {move} hits {_opponent_card.name} for {true_dmg}!'       
                    else:
                        true_dmg = 0
                        message = f'{move_emoji} {move} misses {_opponent_card.name}! 💨'
                
                elif hit_roll <= low_hit and hit_roll > miss_hit:
                    true_dmg = round(true_dmg * .70)
                    message = f'{move_emoji} {move} used! Chips {_opponent_card.name} for {true_dmg}! 💢'
                
                elif hit_roll <= med_hit and hit_roll > low_hit:
                    true_dmg = round(true_dmg)
                    message = f'{move_emoji} {move} used! Connects with {_opponent_card.name} for {true_dmg}! ‼️'
                
                elif hit_roll <= standard_hit and hit_roll > med_hit:
                    true_dmg = round(true_dmg * 1.2)
                    message = f'{move_emoji} {move} used! Hits {_opponent_card.name} for {true_dmg}! 🗯️'
                
                elif hit_roll >= 20:
                    if self.stagger:
                        self.stagger_activated = True
                    if self.universe =="Crown Rift Awakening":
                        true_dmg = round(true_dmg * 3)
                        message = f"🩸 {move_emoji} Blood Awakening! {move} used! Critically Hits {_opponent_card.name} for {true_dmg}!! 💥"
                    else:
                        true_dmg = round(true_dmg * 2)
                        message = f"{move_emoji} {move} used! Critically Hits {_opponent_card.name} for {true_dmg}!! 💥"
                
                else:
                    message = f"{move_emoji} {move} used! Dealt {true_dmg} dmg to {_opponent_card.name}!"

                if self._magic_active and move_element not in ['PHYSICAL', 'RANGED', 'RECOIL']:
                    true_dmg = round(true_dmg + (true_dmg * .40))

                if is_physical_element:
                    if self.stamina > 80:
                        true_dmg = round(true_dmg * 1.5)


                if move_element in _opponent_card.weaknesses and not (hit_roll <= miss_hit):
                    true_dmg = round(true_dmg * 1.6)
                    if summon_used:
                        message = f"{_opponent_card.name} is weak to {move_emoji} {move_element.lower()}! Strong hit for {true_dmg}!"
                    else:
                        message = f"{_opponent_card.name} is weak to {move_emoji} {move_element.lower()}! Strong hit for **{true_dmg}**!"
                
                if not self._talisman == move_element and not self._is_boss and not spirit_crit:
                    if move_element in _opponent_card.resistances and not (hit_roll <= miss_hit) :
                        true_dmg = round(true_dmg * .45)
                        if summon_used:
                            message = f"{_opponent_card.name} is resistant to {move_emoji} {move_element.lower()}. Weak hit for {true_dmg}!"
                        else:
                            message = f"{_opponent_card.name} is resistant to {move_emoji} {move_element.lower()}. Weak hit for **{true_dmg}**!"
                    if move_element in _opponent_card.immunity and not (hit_roll <= miss_hit):
                        true_dmg = 0
                        if summon_used:
                            message = f"{_opponent_card.name} is immune to {move_emoji} {move_element.lower()}. 0 dmg dealt!"
                        else:
                            message = f"{_opponent_card.name} is immune to {move_emoji} {move_element.lower()}. **0** dmg dealt!"
                    if move_element in _opponent_card.repels and not (hit_roll <= miss_hit):
                        if summon_used:
                            self.health = self.health - true_dmg
                            message = f"{_opponent_card.name} repels {true_dmg} {move_emoji} {move_element.lower()} dmg!"
                        else:
                            message = f"{_opponent_card.name} repels **{true_dmg}** {move_emoji} {move_element.lower()} dmg!"
                        does_repel = True
                    if move_element in _opponent_card.absorbs and not (hit_roll <= miss_hit):
                        if summon_used:
                            _opponent_card.health = _opponent_card.health + true_dmg
                            message = f"{_opponent_card.name} absorbs {true_dmg} {move_emoji} {move_element.lower()} dmg!"
                        else:
                            message = f"{_opponent_card.name} absorbs **{true_dmg}** {move_emoji} {move_element.lower()} dmg!"
                        does_absorb = True
                        
                if self._assassin_active and not summon_used:
                    self._assassin_value += 1
                    battle_config.add_to_battle_log(f"(**{crown_utilities.class_emojis['ASSASSIN']}**) **{self.name}**:  Assassin Strike!\n*{self._assassin_attack - self._assassin_value} Left!*")
                    if self._assassin_value == self._assassin_attack:
                        self._assassin_active = False
                else:
                    if not self.used_block:
                        self.stamina = self.stamina - move_stamina
                
                if _opponent_card.damage_check_activated:
                    true_dmg = 5
                    message = f"{_opponent_card.name} is in damage check mode"

                if _opponent_card._heal_active:
                    _opponent_card._heal_value = round(_opponent_card._heal_value + (true_dmg * _opponent_card._heal_buff))

                        
                response = {"DMG": true_dmg, "MESSAGE": message,
                            "CAN_USE_MOVE": can_use_move_flag, "ENHANCE": False, "REPEL": does_repel, "ABSORB": does_absorb, "ELEMENT": move_element, "STAMINA_USED": move_stamina, "SUMMON_USED": summon_used}

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


    def adjust_hit_roll(self, hit_roll, _opponent_card, summon_used, true_dmg, move_element, battle_config, low_hit, med_hit, standard_hit, high_hit, miss_hit):
        if _opponent_card.damage_check_activated:
            hit_roll += 3
            _opponent_card.damage_check_counter += true_dmg
            if not summon_used:
                _opponent_card.damage_check_turns -= 1
            if _opponent_card.damage_check_activated:
                damage_check_message = f"(:vs:)**[[Damage Check] {round(_opponent_card.damage_check_counter)} damage done so far]**"
                battle_config.add_to_battle_log(damage_check_message)
                _opponent_card.damage_check_turns = _opponent_card.damage_check_turns - 1
                if _opponent_card.damage_check_counter >= _opponent_card.damage_check_limit:
                    damage_check_message = f"✅ **[{self.name} passed the Damage Check]**"
                    battle_config.add_to_battle_log(damage_check_message)
                    _opponent_card.damage_check_activated = False
                    _opponent_card.damage_check_counter = 0
                    _opponent_card.damage_check_limit = 0
                    _opponent_card.damage_check_turns = 0
                    _opponent_card.damage_check = False
                elif _opponent_card.damage_check_turns <= 0:
                    _opponent_card.damage_check_activated = False
                    _opponent_card.damage_check_counter = 0
                    _opponent_card.damage_check_limit = 0
                    _opponent_card.damage_check_turns = 0
                    _opponent_card.damage_check = False
                    self.health = 0
                    self.defense = 0
                    self.attack = 0
                    damage_check_message = f"❌ **[{self.name} failed the Damage Check]**"
                    battle_config.add_to_battle_log(damage_check_message)

        if self.universe == "Crown Rift Slayers" and hit_roll <= low_hit:
            hit_roll = hit_roll - 5

        if self._swordsman_active and self.used_resolve and not summon_used:
            if self._critical_strike_count < self._swordsman_value:
                self._critical_strike_count += 1
                hit_roll = 20
                battle_config.add_to_battle_log(f"(**{crown_utilities.class_emojis['SWORDSMAN']}**) **{self.name}**:  Critical Strike!\n*{self._swordsman_value - self._critical_strike_count} Left!*")

        if self.bloodlust_activated:
            hit_roll = hit_roll + 3
            self.health = self.health + (.35 * true_dmg)

        if (move_element == "SPIRIT" or self.stagger) and hit_roll >= 13:
            hit_roll = hit_roll + 7

        if self.universe == "Crown Rift Awakening" and hit_roll > med_hit:
            hit_roll = hit_roll + 3
            
        if self._assassin_active:
            hit_roll = hit_roll + round(hit_roll * .50)
        
        if (_opponent_card.used_block or _opponent_card.used_defend) and hit_roll >= 20:
            hit_roll = 19

        return hit_roll


    def set_battle_arm_messages(self, opponent_card):
        if self.used_resolve:
            self.summon_resolve_message = f"🧬 | {crown_utilities.set_emoji(self.summon_type)} {self.summon_type.capitalize()}"
        
        weapon_emojis = {
            "barrier": "💠",
            "shield": "🌐",
            "parry": "🔄",
            "siphon": "💉"
        }

        self._arm_message = ""
        opponent_card._arm_message = ""
        if opponent_card._barrier_active:
            opponent_card._arm_message += f"{weapon_emojis['barrier']} | {opponent_card._barrier_value} Barrier\n"
        if opponent_card._shield_active:
            opponent_card._arm_message += f"{weapon_emojis['shield']} | {opponent_card._shield_value} Shield\n"
        if opponent_card._parry_active:
            opponent_card._arm_message += f"{weapon_emojis['parry']} | {opponent_card._parry_value} Parry\n"
        if opponent_card._siphon_active:
            opponent_card._arm_message += f"{weapon_emojis['siphon']} | {opponent_card._siphon_value} Siphon\n"
        
        if len(opponent_card._arm_message) > 0:
            opponent_card._arm_message = "\n" + opponent_card._arm_message

        if self._barrier_active:
            self._arm_message += f"{weapon_emojis['barrier']} | {self._barrier_value} Barrier\n"
        if self._shield_active:
            self._arm_message += f"{weapon_emojis['shield']} | {self._shield_value} Shield\n"
        if self._parry_active:
            self._arm_message += f"{weapon_emojis['parry']} | {self._parry_value} Parry\n"
        if self._siphon_active:
            self._arm_message += f"{weapon_emojis['siphon']} | {self._siphon_value} Siphon\n"
        
        if len(self._arm_message) > 0:
            self._arm_message = "\n" + self._arm_message


    def focusing(self, _title, _opponent_title, _opponent_card, battle_config, _co_op_card=None, _co_op_title=None ):
        if self.stamina < self.stamina_required_to_focus:
            self.used_focus = True
            if battle_config.is_tutorial_game_mode and battle_config.tutorial_focus is False:
                # _opponent_card.used_focus = True
                embedVar = discord.Embed(title=f"You've entered :cyclone:**Focus State**!",
                                        description=f"Entering :cyclone:**Focus State** sacrifices a turn to **Heal** and regain **ST (Stamina)**!",
                                        colour=0xe91e63)
                embedVar.add_field(name=":cyclone:**Focusing**",
                                value="Increase **ATK** (🟦) and **DEF** (🟥)!")
                embedVar.set_footer(
                    text="Pay attention to your oppononets ST(Stamina). If they are entering Focus State, you will have the ability to strike twice!")
                
                battle_config._tutorial_message = embedVar

            self.usedsummon = False
            self.focus_count = self.focus_count + 1            

            if battle_config.is_boss_game_mode and battle_config.is_turn not in [1,3]:
                if battle_config._boss_player_focus_message == False:
                    embedVar = discord.Embed(title=f"{battle_config._punish_boss_description}")
                    embedVar.add_field(name=f"{battle_config._arena_boss_description}", value=f"{battle_config._world_boss_description}", inline=False)
                    embedVar.set_footer(text=f"{battle_config._assault_boss_description}")
                    battle_config._boss_embed_message = embedVar
                    battle_config._boss_player_focus_message = True
            elif battle_config.is_boss_game_mode and battle_config.is_turn in [1,3]:
                if battle_config._boss_focus_message == False:
                    embedVar = discord.Embed(title=f"{battle_config._powerup_boss_description}", colour=0xe91e63)
                    embedVar.add_field(name=f"A great aura starts to envelop **{self.name}** ",
                                    value=f"{battle_config._aura_boss_description}")
                    embedVar.set_footer(text=f"{self.name} Says: 'Now, are you ready for a real fight?'")   
                    battle_config._boss_embed_message = embedVar
                    battle_config._boss_focus_message = True
            
            # fortitude or luck is based on health
            fortitude = round(self.health * .1)
            if fortitude <= 50:
                fortitude = 50

            self.stamina = self.stamina_focus_recovery_amount
            health_calculation = round(fortitude)
            if self._heal_active:
                health_calculation = health_calculation + self._heal_value
                if self.health >= self.max_health:
                    self.health = self.max_health
                self._heal_value = 0
            attack_calculation = round((fortitude * (self.tier / 10)) + (.05 * self.attack))
            defense_calculation = round((fortitude * (self.tier / 10)) + (.05 * self.defense))
            
            
            if _title.passive_type:
                if _title.passive_type == "GAMBLE":
                    health_calculation = _title.passive_value
                if _title.passive_type == "BLAST":
                    _opponent_card.health = _opponent_card.health - (_title.passive_value * battle_config.turn_total)
                if _title.passive_type == "SOULCHAIN":
                    self.stamina = self.stamina + _title.passive_value

            if _opponent_title.passive_type:
                if _opponent_title.passive_type == "GAMBLE":
                    health_calculation = _opponent_title.passive_value
                if _opponent_title.passive_type == "BLAST":
                    self.health = self.health - (_opponent_title.passive_value * battle_config.turn_total)
                if _opponent_title.passive_type == "SOULCHAIN":
                    self.stamina = self.stamina + _opponent_title.passive_value
                    
            if self.passive_type == "GAMBLE":
                health_calculation = self.passive_num
            if _opponent_card.passive_type == "GAMBLE":
                health_calculation = _opponent_card.passive_num
                    
            
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
                        health_calculation = round(self.max_health - self.health)
                        self.damage_healed = round(self.damage_healed + health_calculation)
                        self.health = self.max_health
                        
                    else:
                        heal_message = "regained some vitality."
                        message_number = 2
                        self.damage_healed = round(self.damage_healed + health_calculation)
                        self.health = new_health_value
                       
                else:
                    heal_message = f"**{_opponent_card.name}**'s blows don't appear to have any effect!"
                    self.health = self.max_health
                    message_number = 0
            
            if self.universe == "Crown Rift Madness" and not self.used_resolve:
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) 🩸 Madness!\n**{self.name}** focused and {heal_message}\n*+:dagger: {attack_calculation} | +:shield:{defense_calculation}*")
            else:
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) 🌀 **{self.name}** focused and {heal_message}")
            if self.universe == "Crown Rift Madness" and self.used_resolve:
                self.attack = self.attack + attack_calculation
                self.defense = self.defense + defense_calculation
                battle_config.add_to_battle_log(f"(🌀) 🩸 Beast Blood!\n**{self.name}** Gains ATK and DEF\n*+:dagger: {attack_calculation} | +:shield:{defense_calculation}*")
            elif not self.used_resolve:
                if self.universe == "One Piece" and (self.tier in crown_utilities.MID_TIER_CARDS or self.tier in crown_utilities.HIGH_TIER_CARDS):
                    attack_calculation = attack_calculation + round(attack_calculation / 2)
                    defense_calculation = defense_calculation + round(defense_calculation / 2)
                    battle_config.add_to_battle_log(f"(**🌀**) 🩸 Armament Haki !\n**{self.name}**  Gains 2x ATK and DEF\n*+:heart:{health_calculation} | +:dagger: {attack_calculation} | +:shield:{defense_calculation}*")
                elif self.universe != "Crown Rift Madness":
                    battle_config.add_to_battle_log(f"*(🌀) {self.name}\n+:heart:{health_calculation} | +:dagger: {attack_calculation} | +:shield:{defense_calculation}*")
                self.attack = self.attack + attack_calculation
                self.defense = self.defense + defense_calculation
            elif self.used_resolve and self.universe != "Crown Rift Madness":
                battle_config.add_to_battle_log(f"*(🌀) {self.name}\n+:heart:{health_calculation}*")
                
                

            # Resolve Check and Calculation
            if not self.used_resolve and self.used_focus and self.universe == "Digimon":  # Digimon Universal Trait
                if battle_config.is_tutorial_game_mode and _opponent_card.used_resolve is False:
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
                    battle_config.tutorial_message = embedVar

                
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                # Resolve Scaling
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round((.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round((.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.damage_healed = self.damage_healed + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.attack = round(self.attack * 1.5)
                self.defense = round(self.defense * 1.5)
                self.used_resolve = True
                self.usedsummon = False
                if battle_config.turn_total <= 5:
                    self.attack = round(self.attack * 2)
                    self.defense = round(self.defense * 2 )
                    self.health = self.health + 500
                    self.damage_healed = self.damage_healed + 500
                    self.max_health = self.max_health + 500
                    battle_config.add_to_battle_log(f"(**⚡**) **{self.name}** 🩸 Transformation: Mega Digivolution!!!")
                else:
                    battle_config.add_to_battle_log(f"(**⚡**) **{self.name}** 🩸 Transformation: Digivolve")
            #Self Traits
            if self.universe == "League Of Legends":                
                if _opponent_card.health <= (_opponent_card.max_health * .90):
                    turret_shot =  round((_opponent_card.health * .10) + battle_config.turn_total)
                elif _opponent_card.health <= (_opponent_card.max_health * .75):
                    turret_shot = round((_opponent_card.health * .15) + battle_config.turn_total)
                elif _opponent_card.health <= (_opponent_card.max_health * .50):
                    turret_shot = round((_opponent_card.health * .20) + battle_config.turn_total)
                else:
                    turret_shot = round((_opponent_card.health * .05) + battle_config.turn_total)
                self.damage_dealt = self.damage_dealt + turret_shot
                _opponent_card.health = _opponent_card.health - turret_shot
                battle_config.add_to_battle_log(f"(**🌀**) 🩸 Turret Shot hits **{_opponent_card.name}** for **{(turret_shot + battle_config.turn_total)}** Damage 💥")

            elif self.universe == "Dragon Ball Z":
                self.health = self.health + (_opponent_card.stamina * _opponent_card.tier) + battle_config.turn_total
                self.max_health = self.max_health + (_opponent_card.stamina * _opponent_card.tier) + battle_config.turn_total
                battle_config.add_to_battle_log(f"(**🌀**) 🩸 Saiyan Spirit... You heal for **{(_opponent_card.stamina * _opponent_card.tier) + battle_config.turn_total}** ❤️")

            elif self.universe == "Solo Leveling":
                _opponent_card.defense = round(_opponent_card.defense - (50 + battle_config.turn_total))
                summon_increase = 1
                summon_msg = ""
                if self.summon_type not in ['PARRY', 'BARRIER']:
                    summon_increase = (50 + battle_config.turn_total)
                    summon_msg = "Ability Power!"
                    if self.summon_type == "SHIELD":
                        summon_msg = ""
                    
                self.summon_power = self.summon_power + summon_increase
                battle_config.add_to_battle_log(f"(**🌀**) 🩸 Ruler's Authority... Opponent loses **{50 + battle_config.turn_total}** 🛡️ 🔻 Summon gained {summon_increase} {self.summon_type.capitalize()} {summon_msg}")

            elif self.universe == "Black Clover":                
                self.stamina = 100
                self.card_lvl_ap_buff = self.card_lvl_ap_buff + 50 + battle_config.turn_total

                battle_config.add_to_battle_log(f"(**🌀**) 🩸 Mana Zone! **{self.name}** Increased AP & Stamina 🌀")

            elif self.universe == "Death Note":
                if battle_config.turn_total >= (130 + (10 * self.tier)):
                    battle_config.add_to_battle_log(f"(**🌀**) **{_opponent_card.name}** 🩸 had a heart attack and died")
                    
                    _opponent_card.health = -1000
            
            elif self.universe == "One Punch Man":
                low_tier_cards = [1,2]
                mid_tier_cards = [3,4]
                high_tier_cards = [5,6]
                rank = "F"
                ap_boost = 15 * self.tier
                if self.tier == 7:
                    ap_boost = 110
                    rank = ":regional_indicator_s:"
                if self.tier in low_tier_cards:
                    rank = ":regional_indicator_c:"
                if self.tier in mid_tier_cards:
                    rank = ":regional_indicator_b:"
                if self.tier in high_tier_cards:
                    rank = ":regional_indicator_a:"
                self.card_lvl_ap_buff = self.card_lvl_ap_buff + ap_boost
                
                battle_config.add_to_battle_log(f"(**🌀**)  🩸{rank} Rank Hero : **{self.name}** increased AP by **{ap_boost}** :sunny:!")

            #Opponent Traits
            if _opponent_card.universe == "One Punch Man":
                _opponent_card.health = round(_opponent_card.health + 100)
                _opponent_card.max_health = round(_opponent_card.max_health + 100)

                battle_config.add_to_battle_log(f"(**🌀**) 🩸 Hero Reinforcements! **{_opponent_card.name}**  Increased Health & Max Health ❤️")

            elif _opponent_card.universe == "7ds":
                _opponent_card.stamina = _opponent_card.stamina + 60
                fortitude = round(_opponent_card.health * .1)
                if fortitude <= 50:
                    fortitude = 50
                health_calculation = round(fortitude)
                if _opponent_card._heal_active:
                    health_calculation = health_calculation + _opponent_card._heal_value
                    if _opponent_card.health >= _opponent_card.max_health:
                        _opponent_card.health = _opponent_card.max_health
                    _opponent_card._heal_value = 0
                attack_calculation = round((fortitude * (_opponent_card.tier / 10)) + (.05 * _opponent_card.attack))
                defense_calculation = round((fortitude * (_opponent_card.tier / 10)) + (.05 * _opponent_card.defense))
                _opponent_card.attack = _opponent_card.attack + attack_calculation
                _opponent_card.defense = _opponent_card.defense + defense_calculation
                if _opponent_card.health <= _opponent_card.max_health:
                    new_health_value = _opponent_card.health + health_calculation
                    if new_health_value > _opponent_card.max_health:
                        health_calculation = round(_opponent_card.max_health - _opponent_card.health)
                        _opponent_card.damage_healed = round(_opponent_card.damage_healed + health_calculation)
                        _opponent_card.health = _opponent_card.max_health       
                    else:
                        _opponent_card.damage_healed = round(_opponent_card.damage_healed + health_calculation)
                        _opponent_card.health = new_health_value
                else:
                    _opponent_card.health = _opponent_card.max_health
                _opponent_card.usedsummon = False
                if _opponent_card.used_resolve:
                    battle_config.add_to_battle_log(f"(**🌀**) 🩸 Power Of Friendship! 🧬 {_opponent_card.summon_name} Rested, **{_opponent_card.name}** Gained **60** Stamina and Focused!\n*+:heart:{health_calculation} | +:dagger: {attack_calculation} | +:shield:{defense_calculation}*")
                else:
                    battle_config.add_to_battle_log(f"(**🌀**) 🩸 Increase Power!** {_opponent_card.name}** Gained **60** Stamina and Focused!\n*+:heart:{health_calculation} | +:dagger: {attack_calculation} | +:shield:{defense_calculation}*")

            elif _opponent_card.universe == "Souls" and not _opponent_card.used_resolve:
                _opponent_card.attack = round(_opponent_card.attack + (100 + battle_config.turn_total))

                battle_config.add_to_battle_log(f"(**🌀**) 🩸 Phase 1! Combo Recognition! **{_opponent_card.name}** Increased Attack by **{100 + battle_config.turn_total}** 🔺")

            battle_config.turn_total = battle_config.turn_total + 1
            
            if self.universe != "Crown Rift Madness":
                battle_config.next_turn()
            else:
                battle_config.repeat_turn()

    
    def resolving(self, battle_config, opponent_card, player=None, opponent=None):
        if self.defense <= 0:
            self.defense = 25
        if self.attack <= 0:
            self.attack = 25
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

                self.my_hero_academia_buff = self.my_hero_academia_buff_counter * self.focus_count
                self.stamina = 160
                self.health = self.health + resolve_health
                self.damage_healed = self.damage_healed + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.used_resolve = True
                self.usedsummon = False
                
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Quirk Awakening! Ap has been increased by **{self.my_hero_academia_buff}** 🔺")

                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()

            elif self.universe == "YuYu Hakusho":  # My Hero Trait
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
                
                boost = 0
                if self.health >= 0.8 * self.base_max_health:
                    boost = 0.15
                elif self.health <= 0.4 * self.base_max_health:
                    boost = 1
                else:
                    boost = .30

                self.stamina = 160
                self.health = self.health + resolve_health
                self.damage_healed = self.damage_healed + resolve_health
                self.attack = round(self.attack * 2)
                self.yuyu_1ap_buff = round(self.move1ap * boost)
                self.yuyu_2ap_buff = round(self.move2ap * boost)
                self.yuyu_3ap_buff = round(self.move3ap * boost)
                self.defense = 100
                self.used_resolve = True
                self.usedsummon = False
                
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Spirit Resolved! Ap has been increased by **{round(boost)}** 🔺")

                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()

            elif self.universe == "One Piece" and (self.tier in crown_utilities.HIGH_TIER_CARDS):
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

                opponent_card.card_lvl_ap_buff = opponent_card.card_lvl_ap_buff - 150
                if opponent_card.card_lvl_ap_buff <=0:
                    opponent_card.card_lvl_ap_buff = 1

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.damage_healed = self.damage_healed + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.used_resolve = True
                self.usedsummon = False

                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Conquerors Haki!")

                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()

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
                self.damage_healed = self.damage_healed + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                if opponent_card.attack > self.attack:
                    self.attack = opponent_card.attack
                if opponent_card.defense > self.defense:
                    self.defense = opponent_card.defense
                self.used_resolve = True
                self.usedsummon = False

                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Total Concentration Breathing!")
                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()

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
                self.health = self.health + self.naruto_heal_buff
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)

                self.damage_healed = self.damage_healed + resolve_health + self.naruto_heal_buff
                
                self.used_resolve = True
                self.usedsummon = False

                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()

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
                self.usedsummon = False
                health_boost = 100 * self.focus_count
                self.health = self.health + health_boost
                self.damage_healed = self.damage_healed + resolve_health + health_boost

                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Titan Mode! Health increased by **{health_boost}**!")

                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()

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
                self.damage_healed = self.damage_healed + resolve_health
                self.attack = round((self.attack + (2 * resolve_attack_value))* 2)
                self.defense = round(self.defense - resolve_defense_value)
                # if self.defense >= 120:
                # # self.defense = 120
                self.used_resolve = True
                self.usedsummon = False
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Bankai!")

                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()
            
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
                self.usedsummon = False

                if self._gow_resolve:
                    self.damage_healed = self.damage_healed + (self.max_health - self.health)
                    self.health = self.max_health
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Ascension!")
                elif not self._gow_resolve:
                    self.health = round(self.health + (self.max_health / 2))
                    self.damage_healed = self.damage_healed + (self.max_health / 2)
                    self.used_resolve = False
                    self._gow_resolve = True
                    
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Crushed Blood Orb: Health Refill")
                                
                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()
            
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
                self.damage_healed = self.damage_healed + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                
                damage_calculation_response = self.damage_cal(3, battle_config, opponent_card, )
                opponent_card.health = opponent_card.health - damage_calculation_response['DMG']
                self.damage_dealt = self.damage_dealt + damage_calculation_response['DMG']
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Command Seal! {damage_calculation_response['MESSAGE']}")
                
                # self.stamina = 0
                self.used_resolve = True
                self.usedsummon = False
                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()
            
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
                self.usedsummon = False

                evolution_boost = 500 * self.tier
                if battle_config.turn_total >= 50:
                    self.max_health = self.max_health + (evolution_boost * 2)
                    self.health = self.health + (evolution_boost * 2)
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Gigantomax Evolution!!! Gained 2x Defense and **{evolution_boost * 2}** HP!!!")
                elif battle_config.turn_total >= 30:
                    self.max_health = self.max_health + evolution_boost
                    self.health = self.health + evolution_boost
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Mega Evolution!! Gained 2x Defense**{evolution_boost}** HP!")
                else:
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Evolution! Gained 2x Defense")

                self.damage_healed = self.damage_healed + resolve_health + evolution_boost
                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()
            
            else:  # Standard Resolve
                # fortitude or luck is based on health
                fortitude = 0.0
                low = self.health - (self.health * .75)
                high = self.health - (self.health * .66)
                fortitude = round(random.randint(int(low), int(high)))
                #print(fortitude)
                # Resolve Scaling
                if self.defense <= 0:
                    self.defense = 25
                resolve_health = round(fortitude + (.5 * self.resolve_value))
                resolve_attack_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))
                resolve_defense_value = round(
                    (.30 * self.defense) * (self.resolve_value / (.50 * self.defense)))

                self.stamina = self.stamina + self.resolve_value
                self.health = self.health + resolve_health
                self.damage_healed = self.damage_healed + resolve_health
                self.attack = round(self.attack + resolve_attack_value)
                self.defense = round(self.defense - resolve_defense_value)
                self.used_resolve = True
                self.usedsummon = False
                if self.universe == "League Of Legends":
                    opponent_card.health = opponent_card.health - (200 * (self.focus_count + opponent_card.focus_count))
                    self.damage_dealt = self.damage_dealt + (200 * (self.focus_count + opponent_card.focus_count))
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Resolved: Pentakill! Dealing {(200 * (self.focus_count + opponent_card.focus_count))} damage.")
                elif self.universe == "Souls":
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Phase 2: Enhanced Moveset!")
                    self.set_souls_trait()
                else:
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) ⚡ **{self.name}** Resolved!")

                battle_config.turn_total = battle_config.turn_total + 1
                battle_config.next_turn()
            
            if self.is_tank:
                self._shield_value = self._shield_value + (self.tier * 500)
                battle_config.add_to_battle_log(f"({crown_utilities.class_emojis['TANK']}) {self.name} gained **{self._shield_value}** Shield!")

            if self.overwhelming_power:
                self._parry_active = True
                self._parry_value = round(random.randint(10, 20))
                battle_config.add_to_battle_log(f"**[{self.name} is overwhemlingly powerful, parrying the next {str(self._parry_value)} attacks**")
                
            if battle_config.is_boss_game_mode:
                if (battle_config.is_turn == 0 or battle_config.is_turn == 2):
                    if battle_config._boss_resolve_message == False:
                        embedVar = discord.Embed(title=f"{battle_config._rmessage_boss_description}")
                        embedVar.set_footer(text=f"{opponent_card.name} this will not be easy...")
                        battle_config._boss_embed_message = embedVar
                        battle_config._boss_resolve_message = True
                else:
                    if battle_config._boss_player_resolve_message == False:
                        embedVar = discord.Embed(title=f"{opponent_card.name} Rebukes You!\n{battle_config._rebuke_boss_description}")
                        embedVar.set_footer(text=f"{self.name} this is your chance!")
                        battle_config._boss_embed_message = embedVar
                        battle_config._boss_player_resolve_message = True
    
            if self._monstrosity_active:
                battle_config.add_to_battle_log(f"(**{crown_utilities.class_emojis['MONSTROSITY']}**) **{self.name}**: gains 2 Double Strikes!")
            if self._swordsman_active:
                battle_config.add_to_battle_log(f"(**{crown_utilities.class_emojis['SWORDSMAN']}**) **{self.name}**: gains 3 Critical Strikes!")
            

    def usesummon(self, battle_config, opponent_card):
        if (self.used_resolve or self._summoner_active) and not self.usedsummon:
            damage_calculation_response = self.damage_cal(6, battle_config, opponent_card)
            self.usedsummon = True
            if damage_calculation_response['CAN_USE_MOVE']:
                if self.universe == "Persona":
                    dmg = self.damage_cal(1, battle_config, opponent_card)
                    opponent_card.health = opponent_card.health - dmg['DMG']
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **Persona!** 🩸 : **{self.summon_name}** was summoned from **{self.name}'s** soul dealing **{dmg['DMG']}** damage to!\n**{opponent_card.name}** summon disabled!")
                    self.activate_element_check(battle_config, dmg, opponent_card)
                    opponent_card.usedsummon = True
                    self.damage_dealt = self.damage_dealt + damage_calculation_response['DMG']               
                battle_config.repeat_turn()
                return damage_calculation_response
            else:
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) 🧬 **{self.summon_name}** needs a turn to rest...")
                battle_config.repeat_turn()
        else:
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) 🧬 **{self.summon_name}** needs a turn to rest...")
            battle_config.repeat_turn()

    
    def activate_persona_trait(self, battle_config, opponent_card):
        if self.universe == "Persona" and self.used_resolve:
            summon_response = self.usesummon(battle_config, opponent_card)
            self.activate_element_check(battle_config, summon_response, opponent_card)


    def set_talisman(self, battle_config):
        # if normal, apply talisman for basic attack
        # if hard, apply talisman for ultimate attack
        if battle_config.is_normal_difficulty:
            self._talisman = self.move1_element
        
        if battle_config.is_hard_difficulty:
            self._talisman = self.move3_element 

        if not self._talisman:
            self._talisman = "None"


    def use_companion_enhancer(self, battle_config, opponent_card, companion_card):
        self.enhancer_used = True
        dmg = self.damage_cal(6, battle_config, companion_card)
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
                if companion_card.health >= companion_card.max_health:
                    dmg['DMG'] = dmg['DMG'] - (companion_card.health - companion_card.max_health)
                    companion_card.health = companion_card.max_health
            elif companion_card.move4enh == 'LIFE':
                companion_card.health = round(companion_card.health + dmg['DMG'])
                if companion_card.health >= companion_card.max_health:
                    dmg['DMG'] = dmg['DMG'] - round(companion_card.health - companion_card.max_health)
                opponent_card.health = round(self.health - dmg['DMG'])
            elif companion_card.move4enh == 'DRAIN':
                companion_card.stamina = round(companion_card.stamina + dmg['DMG'])
                companion_card.stamina = round(companion_card.stamina - dmg['DMG'])
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
                if companion_card.health > companion_card.max_health:
                    companion_card.health = companion_card.max_health
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
                companion_card.stamina = round(companion_card.stamina + dmg['DMG'])
            elif companion_card.move4enh == 'SLOW':
                tempstam = round(companion_card.stamina + dmg['DMG'])
                companion_card.stamina = round(companion_card.stamina - dmg['DMG'])
                companion_card.stamina = companion_card.stamina
                companion_card.stamina = tempstam
            elif companion_card.move4enh == 'HASTE':
                tempstam = round(companion_card.stamina - dmg['DMG'])
                companion_card.stamina = round(companion_card.stamina + dmg['DMG'])
                companion_card.stamina = companion_card.stamina
                companion_card.stamina = tempstam
            elif companion_card.move4enh == 'SOULCHAIN':
                companion_card.stamina = round(dmg['DMG'])
                companion_card.stamina = companion_card.stamina
            elif companion_card.move4enh == 'GAMBLE':
                companion_card.health = round(dmg['DMG'])
                self.health = companion_card.health
            elif companion_card.move4enh == 'FEAR':
                if companion_card.universe != "Chainsawman":
                    companion_card.max_health = round(companion_card.max_health - (companion_card.max_health * .10))
                    if companion_card.health > companion_card.max_health:
                        companion_card.health = companion_card.max_health
                opponent_card.defense = round(opponent_card.defense - dmg['DMG'])
                opponent_card.attack= round(opponent_card.attack - dmg['DMG'])
                if opponent_card.card_lvl_ap_buff > 0:
                    opponent_card.card_lvl_ap_buff = round(opponent_card.card_lvl_ap_buff - dmg['DMG'])
                if opponent_card.card_lvl_ap_buff <= 0:
                    opponent_card.card_lvl_ap_buff = 1
            elif companion_card.move4enh == 'WAVE':
                opponent_card.health = round(opponent_card.health - dmg['DMG'])
            elif companion_card.move4enh == 'BLAST':
                if dmg['DMG'] >= (companion_card.tier * 100):
                    dmg['DMG'] = (companion_card.tier * 100)
                opponent_card.health = round(opponent_card.health - dmg['DMG'])
            elif companion_card.move4enh == 'CREATION':
                companion_card.max_health = round(companion_card.max_health + dmg['DMG'])
                companion_card.health = round(companion_card.health + dmg['DMG'])
            elif companion_card.move4enh == 'DESTRUCTION':
                opponent_card.max_health = round(opponent_card.max_health - dmg['DMG'])
                if opponent_card.max_health <=1:
                    opponent_card.max_health = 1
            if companion_card.move4enh in ['HLT','LIFE','CREATION']:
                companion_card.damage_healed = companion_card.damage_healed + dmg['DMG']
            if companion_card.move4enh in ['LIFE','BLAST','WAVE','DESTRUCTION']:
                companion_card.damage_dealt = companion_card.damage_dealt + dmg['DMG']
            if companion_card.move4enh in crown_utilities.Stamina_Enhancer_Check or companion_card.move4enh in crown_utilities.Time_Enhancer_Check:
                opponent_card.stamina = opponent_card.stamina

            if companion_card.summon_type in ['RAGE','BRACE','GROWTH']:
                if companion_card.card_lvl_ap_buff >= 1000 + self.card_lvl:
                    battle_config.add_to_battle_log(f"(**🦠**) **{companion_card.name}**: reached their full power!")
            if companion_card.summon_type in ['FEAR']:
                if opponent_card.card_lvl_ap_buff <= 0:
                    battle_config.add_to_battle_log(f"(**🦠**) **{opponent_card.name}**: is at minimal power!")
            else:
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{companion_card.name}** used {companion_card.move4}:👥 Assisting **{self.name}**")
            battle_config.turn_total = battle_config.turn_total + 1
            battle_config.next_turn()
        else:
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {companion_card.name} doesn't have enough Stamina to use this move")
            battle_config.repeat_turn()
    
    
    def activate_death_note_block_ability(self, battle_config):
        if self.universe == "Death Note":
            value = 3
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **Shinigami Eyes** 🩸 ! **{self.name}** Sacrified {round((.10 * self.max_health))}  Max Health to Increase Turn Count by {value + self.tier}")
            self.max_health = round(self.max_health - (.10 * self.max_health))
            if self.health >= self.max_health:
                self.health = self.max_health
            battle_config.turn_total = battle_config.turn_total + self.tier + value


    def activate_aot_block_ability(self, battle_config):
        if self.universe == "Attack On Titan":
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **Rally** 🩸 ! **{self.name}** Gained {(100 * self.tier)} Health & Max Health ❤️")
            self.max_health = round(self.max_health + (100 * self.tier))
            self.health = self.health + (100 * self.tier)


    def activate_black_clover_block_ability(self, battle_config):
        if self.universe == "Black Clover":                
            self.stamina = self.stamina + 70
            self.card_lvl_ap_buff = self.card_lvl_ap_buff + 50
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Charged their stamina, increasing their stamina & ap by 50")


    def activate_bleach_block_ability(self, battle_config, opponent_card):
        if self.universe == "Bleach":
            dmg = self.damage_cal(1, battle_config, opponent_card)
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** Exerted their 🩸 Spiritual Pressure Executing a Basic Attack!")
            if self.universe == "One Piece" and (self.name_tier in crown_utilities.LOW_TIER_CARDS or self.name_tier in crown_utilities.MID_TIER_CARDS or self.name_tier in crown_utilities.HIGH_TIER_CARDS):
                if self.focus_count == 0:
                    dmg['DMG'] = dmg['DMG'] * .6
            
            self.activate_element_check(battle_config, dmg, opponent_card)

    def activate_my_hero_block_ability(self, battle_config):
        if self.universe == "My Hero Academia" and not self.used_block:
            self.my_hero_academia_buff_counter += 20
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 went Plus Ultra, increasing their dormant ap to {self.my_hero_academia_buff_counter}")

    def activate_yuyu_hakusho_block_ability(self, battle_config):
        if self.universe == "Yu Yu Hakusho" and not self.used_resolve:
            defense_increase = 100 * self.tier
            self.defense = self.defense + defense_increase
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 went into a state of meditation, increasing their defense by {defense_increase}")


    def use_block(self, battle_config, opponent_card, co_op_card=None):
        if self.stamina >= 20:
            self.used_block = True
            self.activate_death_note_block_ability(battle_config)
            
            self.activate_aot_block_ability(battle_config)

            self.activate_black_clover_block_ability(battle_config)

            self.activate_bleach_block_ability(battle_config, opponent_card)

            self.activate_my_hero_block_ability(battle_config)

            self.activate_yuyu_hakusho_block_ability(battle_config)
            
            if battle_config.is_co_op_mode and not (battle_config.is_turn == 1 or battle_config.is_turn == 3):
                block_message = f"**{self.name}**: Defended 🛡️ **{co_op_card.name}**"
                self.used_defend = True
            else:
                block_message = f"**{self.name}** Blocked 🛡️"
                self.used_block = True
            self.stamina = self.stamina - 20
            self.defense = round(self.defense * 3)

            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {block_message}")
            battle_config.turn_total = battle_config.turn_total + 1
            battle_config.next_turn()
        else:
            self.stamina = 0
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** is too tired to block.")
            battle_config.repeat_turn()

    
    def use_defend(self, battle_config, companion_card):
        if self.stamina >= 20:
            self.used_defend = True
            self.stamina = self.stamina - 20
            self.defense = round(self.defense * 2)
            
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}**: Defended 🛡️ **{companion_card.name}**")
            battle_config.turn_total = battle_config.turn_total + 1
            battle_config.next_turn()
        else:
            self.stamina = 0
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** is too tired to block.")
            battle_config.repeat_turn()
            
    
    def use_boost(self, battle_config, companion_card=None):
        if self.stamina >= 10:
            if companion_card:
                companion_card.stamina = companion_card.stamina + 10
                companion_card.health = companion_card.health + 50
                boost_message = f"**{self.name}** Boosted **{companion_card.name}** +10 🌀 +100 :heart:"
                self.used_boost = True
                self.stamina = self.stamina - 10
            else:
                self.stamina = self.stamina + 10
                self.health = self.health + 50
                boost_message = f"**{self.name}** Boosted +10 🌀 +100 :heart:"
                self.stamina = self.stamina

            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {boost_message}")   
            battle_config.turn_total = battle_config.turn_total + 1
            battle_config.next_turn()
        else:
            self.stamina = 0
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** is too tired to boost.")
            battle_config.repeat_turn()
    

    def damage_done(self, battle_config, dmg, opponent_card):
        if dmg['CAN_USE_MOVE']:
            if dmg['ENHANCE']:
                if self.move4enh == 'ATK':
                    self.attack = round(self.attack + dmg['DMG'])
                elif self.move4enh == 'DEF':
                    self.defense = round(self.defense + dmg['DMG'])
                elif self.move4enh == 'STAM':
                    self.stamina = round(self.stamina + dmg['DMG'])
                elif self.move4enh == 'HLT':
                    #self.max_health = round(self.max_health + dmg['DMG'])
                    if self.health < self.max_health:
                        self.health = round(self.health + dmg['DMG'])
                        if self.health > self.max_health:
                            dmg['DMG'] = dmg['DMG'] - (self.health - self.max_health)
                            self.health = self.max_health
                elif self.move4enh == 'LIFE':
                    #self.max_health = round(self.max_health + dmg['DMG'])
                    if (self.health + dmg['DMG']) < self.max_health:
                        self.health = round(self.health + dmg['DMG'])
                        opponent_card.health = round(opponent_card.health - dmg['DMG'])
                    else:
                        dmg['DMG'] = round(self.max_health - self.health)
                        self.health = round(self.health + dmg['DMG'])
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
                    self.health = round(self.health - dmg['DMG'])
                    self.attack = round(self.attack + dmg['DMG'])
                elif self.move4enh == 'CRYSTAL':
                    self.health = round(self.health - dmg['DMG'])
                    self.defense = round(self.defense + dmg['DMG'])
                elif self.move4enh == 'GROWTH':
                    self.max_health = round(self.max_health - (self.max_health * .10))
                    if self.health > self.max_health:
                        self.health = self.max_health
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
                    if battle_config.is_dungeon_game_mode:
                        opponent_card.health = round(dmg['DMG']) * 2
                        self.max_health = round(dmg['DMG'])
                    elif battle_config.is_boss_game_mode:
                        opponent_card.health = round(dmg['DMG']) * 3
                        self.max_health = round(dmg['DMG'])
                    else:
                        opponent_card.health = round(dmg['DMG'])
                        self.max_health = round(dmg['DMG'])
                elif self.move4enh == 'FEAR':
                    if self.universe != "Chainsawman":
                        self.max_health = round(self.max_health - (self.max_health * .10))
                        if self.health > self.max_health:
                            self.health = self.max_health
                    opponent_card.defense = round(opponent_card.defense - dmg['DMG'])
                    opponent_card.attack= round(opponent_card.attack - dmg['DMG'])
                    if opponent_card.card_lvl_ap_buff > 0:
                        opponent_card.card_lvl_ap_buff = round(opponent_card.card_lvl_ap_buff - dmg['DMG'])
                    if opponent_card.card_lvl_ap_buff <= 0:
                        opponent_card.card_lvl_ap_buff = 1
                elif self.move4enh == 'WAVE':
                    opponent_card.health = round(opponent_card.health - dmg['DMG'])
                elif self.move4enh == 'BLAST':
                    if dmg['DMG'] >= (self.tier * 100):
                        dmg['DMG'] = (self.tier * 100)
                    opponent_card.health = round(opponent_card.health - dmg['DMG'])
                elif self.move4enh == 'CREATION':
                    self.max_health = round(self.max_health + dmg['DMG'])
                    self.max_health = round(self.max_health + dmg['DMG'])
                elif self.move4enh == 'DESTRUCTION':
                    if dmg['DMG'] >= (self.tier * 100):
                        dmg['DMG'] = (self.tier * 100)
                    opponent_card.max_health = round(opponent_card.max_health - dmg['DMG'])
                    if opponent_card.max_health <=1:
                        opponent_card.max_health = 1

                if self.move4enh in ['HLT','LIFE','CREATION']:
                    self.damage_healed = self.damage_healed + dmg['DMG']
                if self.move4enh in ['LIFE','BLAST','WAVE','DESTRUCTION']:
                    self.damage_dealt = self.damage_dealt + dmg['DMG']
                
                if self.move4enh in crown_utilities.Stamina_Enhancer_Check or self.move4enh in crown_utilities.Time_Enhancer_Check or self.move4enh in crown_utilities.Control_Enhancer_Check:
                    self.stamina = self.stamina

                if self.move4enh in ['RAGE','BRACE','GROWTH'] and self.card_lvl_ap_buff >= 1000 + self.card_lvl:
                    battle_config.add_to_battle_log(f"(**🦠**) **{self.name}**: reached their full power!")
                elif self.move4enh in ['FEAR'] and opponent_card.card_lvl_ap_buff <= 0:
                    battle_config.add_to_battle_log(f"(**🦠**) **{opponent_card.name}**: is at minimal power!")
                else:
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}**: 🦠 {dmg['MESSAGE']}")
                if opponent_card.health <= 0:
                    if opponent_card._final_stand==True:
                        if opponent_card.universe == "Dragon Ball Z":
                            if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                                self._barrier_active = False
                                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** destroys **{opponent_card.name}** 💠 Barrier!\n     0 Barriers remain!")
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{opponent_card.name}** 🩸 Transformation: Last Stand!!!")
                            # print(opponent_card.attack)
                            # print(opponent_card.defense)
                            opponent_card.health = 1 + round(.75 * (opponent_card.attack + opponent_card.defense))
                            if opponent_card.health < 0:
                                opponent_card.health = 100 + round(.75 * (opponent_card.base_attack + opponent_card.base_defense))
                
                            opponent_card.damage_healed = opponent_card.damage_healed + opponent_card.health
                            # print(opponent_card.health)
                            if not opponent_card.used_resolve:
                                if opponent_card.is_tank:
                                    opponent_card._shield_value = opponent_card._shield_value + (opponent_card.tier * 500)
                                    battle_config.add_to_battle_log(f"({crown_utilities.class_emojis['TANK']}) {opponent_card.name} gained **{opponent_card._shield_value}** Shield!")
                            opponent_card.used_resolve = True
                            opponent_card.used_focus = True
                            opponent_card._final_stand = False
                            battle_config.turn_total = battle_config.turn_total + 1
                            battle_config.next_turn()
                    else:
                        opponent_card.health = 0
                        battle_config.turn_total = battle_config.turn_total + 1
                else:
                    battle_config.turn_total = battle_config.turn_total + 1
                    battle_config.next_turn()
            elif dmg['DMG'] == 0 and not dmg['REPEL'] and not dmg['ABSORB']:
                if self._barrier_active and dmg['ELEMENT'] not in ["PSYCHIC"] and not self.is_ranger:
                    if not dmg['SUMMON_USED']:
                        self._barrier_active = False
                        self._barrier_value = 0
                        self._arm_message = ""
                        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** disengaged their barrier to engage with an attack")
                        self.decrease_solo_leveling_temp_values('BARRIER', opponent_card, battle_config)
                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}**: {dmg['MESSAGE']}")
                battle_config.turn_total = battle_config.turn_total + 1
                if not dmg['SUMMON_USED']:
                    battle_config.next_turn()            
            elif not dmg['REPEL'] and not dmg['ABSORB']:
                if dmg['SUMMON_USED']:
                    name = f"🧬 {self.name} summoned **{self.summon_name}**\n"
                else:
                    name = f" **{self.name}:**"
                
                if opponent_card.universe == "Naruto" and opponent_card.stamina < 10:
                    stored_damage = round(dmg['DMG'])
                    opponent_card.naruto_heal_buff = opponent_card.naruto_heal_buff + stored_damage
                    opponent_card.health = opponent_card.health 

                    if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not self.is_ranger:
                        if not dmg['SUMMON_USED']:
                            self._barrier_active = False
                            self._barrier_value = 0
                            self._arm_message = ""
                            battle_config.add_to_battle_log(f"(💠) **{self.name}** disengaged their barrier to engage with an attack")
                            self.decrease_solo_leveling_temp_values('BARRIER', opponent_card, battle_config)
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{opponent_card.name}** 🩸: Substitution Jutsu")
                    if not opponent_card.used_resolve:
                        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) 🩸**{stored_damage}** Hasirama Cells stored. 🩸**{opponent_card.naruto_heal_buff}** total stored.")
                elif opponent_card._barrier_active and dmg['ELEMENT'] not in ["PSYCHIC", "DARK", "GRAVITY"]:
                    if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not self.is_ranger:
                        if not dmg['SUMMON_USED']:
                            self._barrier_active = False
                            self._barrier_value = 0
                            self._arm_message = ""
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** disengaged their barrier to engage with an attack")
                            self.decrease_solo_leveling_temp_values('BARRIER', opponent_card, battle_config)
                    if opponent_card._barrier_value > 1:
                        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} hits **{opponent_card.name}** Barrier 💠 blocking the attack\n{opponent_card._barrier_value - 1} Barriers remain")
                        if opponent_card._barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                            opponent_card._barrier_active = False
                            opponent_card._barrier_value = 0
                            opponent_card._arm_message = ""
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} destroys **{opponent_card.name}** 💠 Barrier")
                            self.decrease_solo_leveling_temp_values_self('BARRIER', battle_config)
                        opponent_card._barrier_value = opponent_card._barrier_value - 1
                    elif opponent_card._barrier_value == 1:
                        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} destroys **{opponent_card.name}** 💠 Barrier")
                        opponent_card._barrier_value = opponent_card._barrier_value - 1
                        opponent_card._barrier_active = False
                        opponent_card._barrier_value = 0
                        opponent_card._arm_message = ""
                        self.decrease_solo_leveling_temp_values_self('BARRIER', battle_config)
                
                elif opponent_card._shield_active and dmg['ELEMENT'] not in ["DARK", "PSYCHIC", "TIME"]:
                    if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not self.is_ranger:
                        if not dmg['SUMMON_USED']:
                            self._barrier_active = False
                            self._barrier_value = 0
                            self._arm_message = ""
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** disengaged their barrier to engage with an attack")
                            self.decrease_solo_leveling_temp_values('BARRIER', opponent_card, battle_config)
                    if dmg['ELEMENT'] == "POISON": #Poison Update
                        if self.poison_dmg <= (100 * self.tier):
                            self.poison_dmg = self.poison_dmg + (15 * self.tier)
                    if dmg['ELEMENT'] == "FIRE":
                        self.burn_dmg = self.burn_dmg + round(dmg['DMG'] * .50)
                    if opponent_card._shield_value > 0:
                        opponent_card._shield_value = opponent_card._shield_value - dmg['DMG']
                        # opponent_card.health = opponent_card.health 
                        if opponent_card._shield_value <= 0:
                            opponent_card._shield_active = False
                            opponent_card._arm_message = ""
                            residue_damage = abs(opponent_card._shield_value)
                            self.decrease_solo_leveling_temp_values_self('SHIELD', battle_config)
                            if opponent_card._parry_active and dmg['ELEMENT'] not in ["EARTH", "DARK", "TIME", "GRAVITY", "LIGHT"]:            
                                if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not self.is_ranger:
                                    if not dmg['SUMMON_USED']:
                                        self._barrier_active = False
                                        self._barrier_value = 0
                                        self._arm_message = ""
                                        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** disengaged their barrier to engage with an attack")
                                        self.decrease_solo_leveling_temp_values('BARRIER', opponent_card, battle_config)
                                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) 🌐 **{opponent_card.name}'s**: Shield Shattered but they were prepared with a Parry!")     
                                if opponent_card._parry_value > 1:
                                    parry_damage = round(residue_damage)
                                    opponent_card.health = round(opponent_card.health - (parry_damage * .75))
                                    self.health = round(self.health - (parry_damage * .40))
                                    self.damage_dealt = self.damage_dealt +  (parry_damage * .75)
                                    opponent_card._parry_value = opponent_card._parry_value - 1
                                    battle_config.add_to_battle_log(f"(**🌐**) **{opponent_card.name}** Parried 🔄 {name}'s attack\nAfter dealing **{round(parry_damage * .75)}** dmg, {self.name} takes {round(parry_damage * .40)} dmg\n{opponent_card._parry_value} Parries left")
                                    if opponent_card._barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                                        opponent_card._barrier_active = False
                                        opponent_card._barrier_value = 0
                                        opponent_card._arm_message = ""
                                        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} destroys **{opponent_card.name}** 💠 Barrier")
                                        self.decrease_solo_leveling_temp_values_self('PARRY', battle_config)
                                elif opponent_card._parry_value == 1:
                                    parry_damage = round(residue_damage)
                                    opponent_card.health = round(opponent_card.health - (parry_damage * .75))
                                    self.health = round(self.health - (parry_damage * .40))
                                    battle_config.add_to_battle_log(f"(**🌐**) {name} penetrated **{opponent_card.name}**'s Final Parry 🔄\nAfter dealing **{round(parry_damage * .75)} dmg**, {self.name} takes {round(parry_damage * .40)} dmg")
                                    opponent_card._parry_value = opponent_card._parry_value - 1
                                    if opponent_card._barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                                        opponent_card._barrier_active = False
                                        opponent_card._barrier_value = 0
                                        opponent_card._arm_message = ""
                                        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} destroys **{opponent_card.name}** 💠 Barrier")
                                        self.decrease_solo_leveling_temp_values_self('BARRIER', battle_config)
                                    opponent_card._parry_active = False
                                    opponent_card._parry_value = 0
                                    opponent_card._arm_message = ""
                                    self.decrease_solo_leveling_temp_values_self('PARRY', battle_config)
                            else:
                                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) 🌐 **{opponent_card.name}'s**: Shield Shattered and they were hit with **{str(residue_damage)} DMG**")
                                opponent_card.health = opponent_card.health - residue_damage
                            self.damage_dealt = self.damage_dealt +  residue_damage
                            if opponent_card._barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                                opponent_card._barrier_active = False
                                opponent_card._barrier_value = 0
                                opponent_card._arm_message = ""
                                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} destroys **{opponent_card.name}** 💠 Barrier")
                                self.decrease_solo_leveling_temp_values_self('BARRIER', battle_config)
                        else:
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} strikes **{opponent_card.name}**'s Shield 🌐\n**{opponent_card._shield_value} Shield** Left!")
                            if opponent_card._barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                                opponent_card._barrier_active = False
                                opponent_card._barrier_value = 0
                                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} destroyed **{opponent_card.name}**'s 💠 Barrier! No Barriers remain!")
                                self.decrease_solo_leveling_temp_values_self('BARRIER', battle_config)
                
                elif opponent_card._parry_active and dmg['ELEMENT'] not in ["EARTH", "DARK", "TIME", "GRAVITY", "LIGHT"]:                    
                    if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not self.is_ranger:
                        if not dmg['SUMMON_USED']:
                            self._barrier_active = False
                            self._barrier_value = 0
                            self._arm_message = ""
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** disengaged their barrier to engage with an attack")
                            self.decrease_solo_leveling_temp_values('BARRIER', opponent_card, battle_config)
                    if opponent_card._parry_value > 1:
                        parry_damage = round(dmg['DMG'])
                        opponent_card.health = round(opponent_card.health - (parry_damage * .75))
                        self.health = round(self.health - (parry_damage * .40))
                        self.damage_dealt = self.damage_dealt +  (parry_damage * .75)
                        opponent_card._parry_value = opponent_card._parry_value - 1
                        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{opponent_card.name}** Parried 🔄 {name}'s attack\nAfter dealing **{round(parry_damage * .75)}** dmg, {self.name} takes {round(parry_damage * .40)} dmg\n{opponent_card._parry_value} Parries left")
                        if opponent_card._barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                            opponent_card._barrier_active = False
                            opponent_card._barrier_value = 0
                            opponent_card._arm_message = ""
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} destroys **{opponent_card.name}** 💠 Barrier")
                            self.decrease_solo_leveling_temp_values_self('PARRY', battle_config)
                    elif opponent_card._parry_value == 1:
                        parry_damage = round(dmg['DMG'])
                        opponent_card.health = round(opponent_card.health - (parry_damage * .75))
                        self.health = round(self.health - (parry_damage * .40))
                        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} penetrated **{opponent_card.name}**'s Final Parry 🔄\nAfter dealing **{round(parry_damage * .75)} dmg**, {self.name} takes {round(parry_damage * .40)} dmg")
                        opponent_card._parry_value = opponent_card._parry_value - 1
                        if opponent_card._barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                            opponent_card._barrier_active = False
                            opponent_card._barrier_value = 0
                            opponent_card._arm_message = ""
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) {name} destroys **{opponent_card.name}** 💠 Barrier")
                            self.decrease_solo_leveling_temp_values_self('BARRIER', battle_config)
                        opponent_card._parry_active = False
                        opponent_card._parry_value = 0
                        opponent_card._arm_message = ""
                        self.decrease_solo_leveling_temp_values_self('PARRY', battle_config)
                
                else:
                    if self.universe == "One Piece" and (self.tier in crown_utilities.LOW_TIER_CARDS or self.tier in crown_utilities.MID_TIER_CARDS or self.tier in crown_utilities.HIGH_TIER_CARDS):
                        if self.focus_count == 0:
                            dmg['DMG'] = dmg['DMG'] * .6

                    if self._siphon_active:
                        siphon_damage = (dmg['DMG'] * .15) + self._siphon_value
                        self.damage_healed = self.damage_healed + (dmg['DMG'] * .15) + self._siphon_value
                        self.health = round(self.health + siphon_damage)
                        if self.health >= self.max_health:
                            self.health = self.max_health
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}**: 💉 Siphoned **Full Health!**")
                        else:
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}**: 💉 Siphoned **{round(siphon_damage)}** Health!")
                    
                    if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not self.is_ranger:
                        if not dmg['SUMMON_USED']:
                            self._barrier_active = False
                            self._barrier_value = 0
                            self._arm_message = ""
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** **{self.name}** disengaged their barrier to engage with an attack")

                    self.activate_element_check(battle_config, dmg, opponent_card)
                battle_config.add_to_battle_log(self.set_poison_hit(opponent_card))
                    # battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}:** {dmg['MESSAGE']}")
                if self.health <= 0:
                    if self._final_stand==True:
                        if self.universe == "Dragon Ball Z":
                            if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not self.is_ranger:
                                if not dmg['SUMMON_USED']:
                                    self._barrier_active = False
                                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** **{self.name}** disengaged their barrier to engage with an attack")
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸 Transformation: Last Stand!!!")
                            # print(opponent_card.attack)
                            # print(opponent_card.defense)
                            self.health = 1 + round(.75 * (self.attack + self.defense))
                            if self.health < 0:
                                self.health = 100 + round(.75 * (self.base_attack + self.base_defense))
                
                            self.damage_healed = self.damage_healed + self.health
                            # print(opponent_card.health)
                            if not self.used_resolve:
                                if self.is_tank:
                                    self._shield_value = self._shield_value + (self.tier * 500)
                                    battle_config.add_to_battle_log(f"({crown_utilities.class_emojis['TANK']}) {self.name} gained **{self._shield_value}** Shield!")
                            self.used_resolve = True
                            self.used_focus = True
                            self._final_stand = False
                
                if opponent_card.health <= 0:
                    if opponent_card._final_stand==True:
                        if opponent_card.universe == "Dragon Ball Z":
                            if self._barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not self.is_ranger:
                                if not dmg['SUMMON_USED']:
                                    self._barrier_active = False
                                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** **{self.name}** disengaged their barrier to engage with an attack")
                            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{opponent_card.name}** 🩸 Transformation: Last Stand!!!")
                            # print(opponent_card.attack)
                            # print(opponent_card.defense)
                            opponent_card.health = 1 + round(.75 * (opponent_card.attack + opponent_card.defense))
                            if opponent_card.health < 0:
                                opponent_card.health = 100 + round(.75 * (opponent_card.base_attack + opponent_card.base_defense))
                
                            opponent_card.damage_healed = opponent_card.damage_healed + opponent_card.health
                            # print(opponent_card.health)
                            if not opponent_card.used_resolve:
                                if opponent_card.is_tank:
                                    opponent_card._shield_value = opponent_card._shield_value + (opponent_card.tier * 500)
                                    battle_config.add_to_battle_log(f"({crown_utilities.class_emojis['TANK']}) {opponent_card.name} gained **{opponent_card._shield_value}** Shield!")
                            opponent_card.used_resolve = True
                            opponent_card.used_focus = True
                            opponent_card._final_stand = False
                            battle_config.turn_total = battle_config.turn_total + 1
                            battle_config.next_turn()
                    elif opponent_card.regeneration:
                        #print("Regeneration activated")
                        if not opponent_card.regeneration_activated:
                            if battle_config.turn_total >= 80:
                                opponent_card.regeneration_activated = True
                                opponent_card.health = opponent_card.max_base_health
                                battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{opponent_card.name}** took a fatal blow but then miraculously [ Regeneration: Activated]!")
                                battle_config.turn_total = battle_config.turn_total + 1
                                battle_config.next_turn()
                    else:
                        opponent_card.health = 0
                        battle_config.turn_total = battle_config.turn_total + 1
                
                else:
                    battle_config.turn_total = battle_config.turn_total + 1
                    if not dmg['SUMMON_USED']:
                        battle_config.next_turn()
            else:
                if dmg['REPEL']:
                    self.health = self.health - dmg['DMG']
                elif dmg['ABSORB']:
                    opponent_card.health = opponent_card.health + dmg['DMG']
                if dmg['SUMMON_USED']:
                    name = f"🧬 {self.name} summoned **{self.summon_name}**\n"
                else:
                    name = f"(**{battle_config.turn_total}**) **{self.name}:**"
                battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}")
                battle_config.turn_total = battle_config.turn_total + 1
                if not dmg['SUMMON_USED']:
                    battle_config.next_turn()
        else:
            print(f"End of damage_done")
            battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}**: Not enough Stamina to use this ability.")
            battle_config.repeat_turn()


    def activate_element_check(self, battle_config, dmg, opponent_card):
        if dmg['REPEL']:
            self.health = self.health - dmg['DMG']
        elif dmg['ABSORB']:
            opponent_card.health = opponent_card.health + dmg['DMG']

        if dmg['SUMMON_USED']:
            name = f"🧬 {self.name} summoned **{self.summon_name}**\n"
        else:
            name = f"(**{battle_config.turn_total}**) **{self.name}:**"

        if dmg['ELEMENT'] == "WATER":
            if self.move1_element == "WATER":
                self.basic_water_buff = self.basic_water_buff + 100
            if self.move2_element == "WATER":
                self.special_water_buff = self.special_water_buff + 100
            if self.move3_element == "WATER":
                self.ultimate_water_buff = self.ultimate_water_buff + 100
            self.water_buff = self.water_buff + 100
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*The Tide Stirs +{self.water_buff}*")
        
        elif dmg['ELEMENT'] == "TIME":
            if self.stamina <= 50:
                self.stamina = 0
                self.card_lvl_ap_buff = self.card_lvl_ap_buff + (2 * battle_config.turn_total)
            self.used_block = True
            self.defense = round(self.defense * 4)
            battle_config.turn_total = battle_config.turn_total + 3
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*Time speeds forward +3 turns!*")
            # battle_config.add_to_battle_log(f"**{self.name}** moved time forward +3 turns!")
            opponent_card.health = opponent_card.health - (dmg['DMG'] * (battle_config.turn_total / 100))

        elif dmg['ELEMENT'] == "EARTH":
            self._shield_active = True
            if self._shield_value <= 0:
                self._shield_value = 0
            self.defense = self.defense + (dmg['DMG'] * .30)
            self._shield_value = self._shield_value + round(dmg['DMG'] * .30)
            self.add_solo_leveling_temp_values('SHIELD', opponent_card)
            if self._shield_value <= 0:
                self._shield_value = 0
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} formed a 🌐 {str(self._shield_value)} Shield*")
            # battle_config.add_to_battle_log(f"*{self.name} erected a 🌐 {str(self._shield_value)} Shield*")
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "DEATH":
            self.attack = self.attack + (dmg['DMG'] * .30)
            opponent_card.max_health = opponent_card.max_health - round(dmg['DMG'] * .30)
            if opponent_card.health > opponent_card.max_health:
                opponent_card.health = opponent_card.max_health
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} reaped {str(round(dmg['DMG'] * .30))} Health from {opponent_card.name}*")

        elif dmg['ELEMENT'] == "LIGHT":
            self.stamina = round(self.stamina + (dmg['STAMINA_USED'] / 2))
            self.attack = self.attack + (dmg['DMG'] * .30)
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} Illuminated! Gain {round((dmg['DMG'] * .30))} ATK*")

        elif dmg['ELEMENT'] == "DARK":
            opponent_card.stamina = opponent_card.stamina - 15
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{opponent_card.name} lost 15 Stamina*")

        elif dmg['ELEMENT'] == "PHYSICAL":
            self.physical_meter = self.physical_meter + 1
            if self.physical_meter == 2:
                self._parry_active = True
                self._parry_value = self._parry_value + 1
                self.add_solo_leveling_temp_values('PARRY', opponent_card)
                self.physical_meter = 0
                battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} prepares to Parry 🔄 the next attack*")
            else:
                 battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}")
            opponent_card.health = opponent_card.health - dmg['DMG']
            
        elif dmg['ELEMENT'] == "RANGED":
            self.ranged_meter = self.ranged_meter + 1
            if self.ranged_meter == 2:
                battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} takes aim...*")
            elif self.ranged_meter == 3:
                self.ranged_meter = 0
                self.ranged_hit_bonus = self.ranged_hit_bonus + 1
                battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} accurary Increased by {self.ranged_hit_bonus * 5}%*")
            else:
                 battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}")
            opponent_card.health = opponent_card.health - dmg['DMG']

        elif dmg['ELEMENT'] == "LIFE":
            self.max_health = self.max_health + round(dmg['DMG'] * .35)
            self.health = self.health + round((dmg['DMG'] * .35))
            opponent_card.health = round(opponent_card.health - dmg['DMG'])
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} gained {str(round(dmg['DMG'] * .35))} Health*")

        elif dmg['ELEMENT'] == "RECOIL":
            self.health = self.health - (dmg['DMG'] * .40)
            if self.health <= 0:
                self.health = 1
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} took {str(round(dmg['DMG'] * .40))} Recoil Damage*")

        elif dmg['ELEMENT'] == "PSYCHIC":
            self.barrier_meter = self.barrier_meter + 1
            if self.barrier_meter == 3:
                self._barrier_active = True
                self._barrier_value = self._barrier_value + 1
                self.add_solo_leveling_temp_values('BARRIER', opponent_card)
                self.barrier_meter = 0
                battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} projects a Barrier 💠 to block next attack*")
            else:    
                battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}")
                # battle_config.add_to_battle_log(f"*{self.name} projects a Barrier 💠 to block next attack*")

            opponent_card.defense = opponent_card.defense - (dmg['DMG'] * .15)
            opponent_card.attack = opponent_card.attack - (dmg['DMG'] * .15)
            opponent_card.health = opponent_card.health - dmg['DMG']
            if opponent_card.defense <= 25:
                opponent_card.defense = 25
            if opponent_card.attack <= 25:
                opponent_card.attack = 25

        elif dmg['ELEMENT'] == "FIRE":
            self.burn_dmg = self.burn_dmg + round(dmg['DMG'] * .50)
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}")

        elif dmg['ELEMENT'] == "ELECTRIC":
            self.shock_buff = self.shock_buff +  (dmg['DMG'] * .20)
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} gained {str(round(dmg['DMG'] * .20))} AP*")

        elif dmg['ELEMENT'] == "POISON":
            if self.poison_dmg <= (200 * self.tier):
                self.poison_dmg = self.poison_dmg + (15 * self.tier)
                if self.poison_dmg > (200 * self.tier):
                   self.poison_dmg = (200 * self.tier)
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}")

        elif dmg['ELEMENT'] == "ICE":
            self.ice_counter = self.ice_counter + 1
            if self.ice_counter == 2:
                self.freeze_enh = True
                self.ice_counter = 0
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}")

        elif dmg['ELEMENT'] == "BLEED":
            self.bleed_damage_counter = self.bleed_damage_counter + 1
            if self.bleed_damage_counter == 2:
                self.bleed_hit = True
                self.bleed_damage_counter = 0
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}")

        elif dmg['ELEMENT'] == "GRAVITY":
            battle_config.turn_total = battle_config.turn_total - 3
            if (battle_config.turn_total - 3) < 0:
                battle_config.turn_total = 0
            self.gravity_hit = True
            opponent_card.health = opponent_card.health - dmg['DMG']
            opponent_card.defense = opponent_card.defense - (dmg['DMG'] * .20)
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}\n*{self.name} has slowed down time -3 turns*")
        
        else:
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"{name} {dmg['MESSAGE']}")
            
        self.element_selection.append(dmg['ELEMENT'])
        self.damage_dealt = self.damage_dealt + dmg['DMG']
        opponent_card.damage_recieved = opponent_card.damage_recieved + dmg['DMG']



    def reset_stats_to_limiter(self, _opponent_card):
        if self.card_lvl_ap_buff > 1000 + self.card_lvl:
            self.card_lvl_ap_buff = 1000 + self.card_lvl
        
        if _opponent_card.card_lvl_ap_buff > 1000 + _opponent_card.card_lvl:
            _opponent_card.card_lvl_ap_buff = 1000 + _opponent_card.card_lvl
            
        if self.card_lvl_ap_buff < 0:
            self.card_lvl_ap_buff = 1
        
        if _opponent_card.card_lvl_ap_buff < 0:
            _opponent_card.card_lvl_ap_buff = 1
        
        if self.attack <= 25:
            self.attack = 25
        
        if self.defense <= 30:
            self.defense = 30
        
        if self.attack > 9999:
            self.attack = 9999
        
        if self.defense > 9999:
            self.defense = 9999
        
        if _opponent_card.attack > 9999:
            _opponent_card.attack = 9999
        
        if _opponent_card.defense > 9999:
            _opponent_card.defense = 9999
    
        if self.health >= self.max_health:
            self.health = self.max_health
            
        if _opponent_card.health >= _opponent_card.max_health:
            _opponent_card.health = _opponent_card.max_health
        
        if self.used_resolve and self.universe == "Souls":
            self.move1ap = self.move2base + round(self.card_lvl_ap_buff + self.shock_buff + self.special_water_buff + self.arbitrary_ap_buff + self.yuyu_1ap_buff + self.my_hero_academia_buff)
            self.move2ap = self.move3base + round(self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff + self.yuyu_2ap_buff + self.my_hero_academia_buff)
            self.move3ap = self.move3base + round(self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff + self.yuyu_3ap_buff + self.my_hero_academia_buff)
        else:
            self.move1ap = self.move1base + round(self.card_lvl_ap_buff + self.shock_buff + self.basic_water_buff + self.arbitrary_ap_buff + self.yuyu_1ap_buff + self.my_hero_academia_buff)
            self.move2ap = self.move2base + round(self.card_lvl_ap_buff + self.shock_buff + self.special_water_buff + self.arbitrary_ap_buff + self.yuyu_2ap_buff + self.my_hero_academia_buff)
            self.move3ap = self.move3base + round(self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff + self.yuyu_3ap_buff + self.my_hero_academia_buff)
        
        # _opponent_card.move1ap = _opponent_card.list(self.m1.values())[0] + _opponent_card.card_lvl_ap_buff + _opponent_card.shock_buff + _opponent_card.basic_water_buff + _opponent_card.arbitrary_ap_buff
        # _opponent_card.move2ap = _opponent_card.list(self.m2.values())[0] + _opponent_card.card_lvl_ap_buff + _opponent_card.shock_buff + _opponent_card.basic_water_buff + _opponent_card.arbitrary_ap_buff
        # _opponent_card.move3ap = _opponent_card.list(self.m3.values())[0] + _opponent_card.card_lvl_ap_buff + _opponent_card.shock_buff + _opponent_card.basic_water_buff + _opponent_card.arbitrary_ap_buff

 
    def get_boss_tactics(self, battle_config):
        if self._is_boss or battle_config.is_raid_scenario:
            self.tactics = battle_config._boss_tactics
            if self.tactics:
                if "ENRAGED" in self.tactics:
                    self.enraged = True
                if "OVERWHELMING_POWER" in self.tactics:
                    self.overwhelming_power = True
                if "REGENERATION" in self.tactics:
                    self.regeneration = True
                if "DEATH_BLOW" in self.tactics:
                    self.death_blow = True
                if "ALMIGHTY_WILL" in self.tactics:
                    self.almighty_will = True
                    self.almighty_will_turns = [1, 5, 9, 10, 14, 15, 19, 20, 24, 25, 40, 45, 53, 54, 55, 74, 75, 95, 98, 100, 101]
                if "STAGGER" in self.tactics:
                    self.stagger = True
                if "INTIMIDATION" in self.tactics:
                    self.intimidation = True
                    self.intimidation_turns = random.randint(1, 5)
                if "BLOODLUST" in self.tactics:
                    self.bloodlust = True
                if "PETRIFIED_FEAR" in self.tactics:
                    self.petrified_fear = True
                    self.petrified_fear_turns = random.randint(1, 5)
                if "DAMAGE_CHECK":
                    self.damage_check = True
                    self.damage_check_limit = round(random.randint(1000, 2500))




    def activate_card_passive(self, player2_card, battle_config):
        if self.passive_type:
            value_for_passive = self.tier * .9
            flat_value_for_passive = 10 * self.tier
            if self.passive_type in ["FEAR", "GROWTH"]:
                flat_value_for_passive = 7 * self.tier
            if self.passive_type in ['ATK', 'DEF']:
                value_for_passive = value_for_passive * 2
            stam_for_passive = 5 * (self.tier * .5)
            if self.passive_type == "HLT":
                if self.max_health > self.health:
                    self.health = round(round(self.health + ((value_for_passive / 100) * self.health)))
            if self.passive_type == "CREATION":
                self.max_health = round(round(self.max_health + ((value_for_passive / 100) * self.max_health)))
            if self.passive_type == "DESTRUCTION":
                player2_card.max_health = round(round(player2_card.max_health - ((value_for_passive / 100) * player2_card.max_health)))
            if self.passive_type == "LIFE":
                dmg = round((value_for_passive / 100) * player2_card.health)
                if (self.health + dmg ) < self.max_health:
                    self.health = round(self.health + dmg)
                    player2_card.health = player2_card.health - dmg
                else:
                    dmg = round(self.max_health - self.health)
                    self.health = round(self.health + dmg)
                    player2_card.health = player2_card.health - dmg
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
                    if self.health > self.max_health:
                        self.health = self.max_health
                player2_card.defense = player2_card.defense - flat_value_for_passive
                player2_card.attack = player2_card.attack - flat_value_for_passive
                if player2_card.card_lvl_ap_buff > 0:
                    player2_card.card_lvl_ap_buff = player2_card.card_lvl_ap_buff - flat_value_for_passive
                if player2_card.card_lvl_ap_buff <= 0:
                    player2_card.card_lvl_ap_buff = 1
            if self.passive_type == "GROWTH":
                self.max_health = self.max_health - (self.max_health * .03)
                if self.health > self.max_health:
                    self.health = self.max_health
                self.defense = self.defense + flat_value_for_passive
                self.attack = self.attack + flat_value_for_passive
                self.card_lvl_ap_buff = self.card_lvl_ap_buff + flat_value_for_passive
            if self.passive_type == "SLOW":
                battle_config.turn_total = battle_config.turn_total - self.passive_num
                if battle_config.turn_total <= 0:
                    battle_config.turn_total = 0
            if self.passive_type == "HASTE":
                battle_config.turn_total = battle_config.turn_total + self.passive_num
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
                if battle_config.turn_total % 10 == 0:
                    player2_card.health = round(player2_card.health - 100)
                    value_for_passive = 100
            if  self.passive_type == "SOULCHAIN":
                self.stamina_focus_recovery_amount  = self.passive_num #hello1
                player2_card.stamina_focus_recovery_amount = self.passive_num
                
            if self.passive_type in ['HLT','CREATION']:
                self.damage_healed = self.damage_healed + ((value_for_passive / 100) * self.health )
            if self.passive_type in ['BLAST','WAVE','DESTRUCTION']:       
                self.damage_dealt = self.damage_dealt + value_for_passive 
            if self.passive_type == "DESTRUCTION":
                self.damage_dealt = self.damage_dealt + ((value_for_passive /100) * player2_card.max_health)
            if self.passive_type == "LIFE":
                self.damage_dealt = self.damage_dealt + dmg
                self.damage_healed = self.damage_healed + dmg
        
                
                #destruction
            
    def activate_chainsawman_trait(self, battle_config):
        if self.universe == "Chainsawman":
            if self.health <= (self.max_health * .50):
                if self._chainsawman_activated == False:
                    self._chainsawman_activated = True
                    self.defense = self.defense * 2
                    self.attack = self.attack * 2
                    self.max_health = self.max_health * 2
                    battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{self.name}** 🩸's Devilization")


                        
    def set_stat_icons(self):
        if self.used_focus:
            self.focus_icon = '💖'
        if self.used_resolve:
            self.resolve_icon = '⚡'
                
    def get_performance_stats(self):
        if len(self.passive_name) > 18:
            self.passive_name = self.passive_name[:15] + "..."
        if round(self.health) == round(self.max_health):
            return f"**Current Stats**\n{self.focus_icon} | **{round(self.health)}** *Health*\n{self.resolve_icon} | **{self.stamina}** *Stamina*\n🩸 | *{self.passive_name}* **{self.passive_type.title()} {self.passive_num}{crown_utilities.passive_enhancer_suffix_mapping[self.passive_type]}**"
        return f"**Current Stats**\n{self.focus_icon} | **{round(self.health)}** / *{round(self.max_health)} Health*\n{self.resolve_icon} | **{self.stamina}** *Stamina*\n🩸 | *{self.passive_name}* **{self.passive_type.title()} {self.passive_num}{crown_utilities.passive_enhancer_suffix_mapping[self.passive_type]}**"
    
    def get_perfomance_header(self, player_title):
        if len(player_title.name) > 18:
            player_title.name = player_title.name[:15] + "..."
        if self._arm_message != "":
            return f"{self.get_performance_stats()}\n{player_title.get_title_icon(self.universe)} | *{player_title.name}* **{player_title.passive_type.title()} {player_title.passive_value}{crown_utilities.title_enhancer_suffix_mapping[player_title.passive_type]}**\n**{self._arm_message}**"
        else:
            return f"{self.get_performance_stats()}\n{player_title.get_title_icon(self.universe)} | *{player_title.name}* **{player_title.passive_type.title()} {player_title.passive_value}{crown_utilities.title_enhancer_suffix_mapping[player_title.passive_type]}**"
    
    def get_performance_moveset(self):
        if len(self.move1) > 18:
            self.move1 = self.move1[:15] + "..."
        if len(self.move2) > 18:
            self.move2 = self.move2[:15] + "..."
        if len(self.move3) > 18:
            self.move3 = self.move3[:15] + "..."
        if len(self.move4) > 18:
            self.move4 = self.move4[:15] + "..."
        if self.used_resolve:
            return f"{self.move1_emoji} 10 | *{self.move1}* **{self.move1ap}**\n{self.move2_emoji} 30 | *{self.move2}* **{self.move2ap}**\n{self.move3_emoji} 80 | *{self.move3}* **{self.move3ap}**\n:microbe: 20 | *{self.move4}* **{self.move4enh.title()} {self.move4ap}**\n*{self.summon_resolve_message}*"
        else:
            return f"{self.move1_emoji} 10 | *{self.move1}* **{self.move1ap}**\n{self.move2_emoji} 30 | *{self.move2}* **{self.move2ap}**\n{self.move3_emoji} 80 | *{self.move3}* **{self.move3ap}**\n:microbe: 20 | *{self.move4}* **{self.move4enh.title()} {self.move4ap}**"
        
def get_card(url, cardname, cardtype):
        try:
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
            
