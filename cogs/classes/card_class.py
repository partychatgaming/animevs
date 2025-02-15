import unique_traits as ut
import crown_utilities
import custom_logging
import stats
import interactions
import requests
import textwrap
import ai
import db
import random
from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji
from io import BytesIO
from cogs.universe_traits.naruto import substitution_jutsu, hashirama_cells
from cogs.universe_traits.dbz import final_stand, saiyan_spirit
from cogs.universe_traits.chainsawman import devils_endurance, contracts, contract_fulfilled
from cogs.universe_traits.demon_slayer import total_concentration_breathing, demon_slayer_blitz
from cogs.universe_traits.one_piece import conquerors_haki, armament
from cogs.universe_traits.yuyu_hakusho import spirit_resolved, meditation
from cogs.universe_traits.my_hero_academia import plus_ultra, quirk_awakening, activate_my_hero_academia_trait
from cogs.universe_traits.aot import titan_mode, rally, omnigear
from cogs.universe_traits.bleach import first_release, spiritual_pressure
from cogs.universe_traits.god_of_war import acension
from cogs.universe_traits.fate import command_seal
from cogs.universe_traits.pokemon import evolutions
from cogs.universe_traits.league_of_legends import pentakill, turret_shot
from cogs.universe_traits.souls import souls_resolve, combo_recognition
from cogs.universe_traits.death_note import shinigami_eyes, scheduled_death
from cogs.universe_traits.black_clover import grimoire, mana_zone
from cogs.universe_traits.fairytail import unison_raid, concentration
from cogs.universe_traits.digimon import digivolve
from cogs.universe_traits.solo_leveling import rulers_authority, add_solo_leveling_temp_values, decrease_solo_leveling_temp_values, decrease_solo_leveling_temp_values_self
from cogs.universe_traits.one_punch_man import rank_hero, hero_reinforcements
from cogs.universe_traits.seven_deadly_sins import increase_power
from cogs.universe_traits.persona import summon_persona, summon_blitz
from cogs.universe_traits.overlord import fear_aura, fear, fear_duration_check
from cogs.universe_traits.jujutsu_kaisen import cursed_energy, cursed_energy_reset, domain_expansion, domain_expansion_check
from cogs.universe_traits.slime import  skill_evolution, summon_slime, beezlebub
from cogs.universe_traits.fma import philosopher_stone, equivalent_exchange, equivalent_exchange_resolve
from cogs.universe_traits.soul_eater import soul_eater, soul_resonance, meister

class Card:
    try:
        def __init__(self, name, path, price, available, skin_for, max_health, health, max_stamina, stamina, moveset, attack, defense, card_type, passive, speed, universe, tier, weaknesses, resistances, repels, absorbs, immunity, gif, fpath, rname, rpath, is_boss, card_class, drop_style, descriptions):
            self.name = name
            self.fpath= fpath
            self.rpath = rpath
            self.rname = rname
            self.gif = gif
            self.path = path
            self.price = price
            self.available = available
            self.skin_for = skin_for
            self.max_health = max_health
            self.descriptions = descriptions
            self.health = health
            self.health_color = crown_utilities.health_color(self.health, self.max_health)
            self.max_stamina = max_stamina
            self.stamina = stamina
            self.moveset = moveset
            self.attack = attack
            self.defense = defense
            self.type = card_type
            self.passive = passive # card passives are deprecated but don't delete
            self.speed = speed
            self.evasion = 0
            self.evasion_message = ""
            self.universe = universe
            self.universe_crest = crown_utilities.crest_dict[self.universe]
            self.tier = tier
            self.weaknesses = weaknesses
            self.resistances = resistances
            self.repels = repels
            self.absorbs = absorbs
            self.immunity = immunity
            self.base_attack  = attack
            self.base_defense = defense
            self.base_health = health
            self.card_class = card_class
            self.drop_style = drop_style
            self.drop_emoji = ""
            self.is_tale_drop = False
            self.is_dungeon_drop = False
            self.is_scenario_drop = False
            self.is_skin_drop = False
            self.is_boss_drop = False
            self.is_destiny_drop = False
            self.is_raid_drop = False
            self.is_tactician = False
            self.is_fighter = False
            self.is_mage = False
            self.is_ranger = False
            self.is_tank = False
            self.is_healer = False
            self.is_assassin = False
            self.is_swordsman = False
            self.is_summoner = False
            self.card_id = 0
            self.is_monstrosity = False
            self.fighter_bonus = 0
            self.ranger_bonus = 0
            self.class_tutorial_message = ""
            self.class_tutorial_message_r = ""
            self.value = 0
            self.p_value = 0 
            if self.drop_style == "TALES":
                self.is_tale_drop = True
                self.drop_emoji = f"🎴"
            elif self.drop_style == "DUNGEON":
                self.is_dungeon_drop = True
                self.drop_emoji = f"👺"
            elif self.drop_style == "RAID":
                self.is_raid_drop = True
                self.drop_emoji = f"💀"
            elif self.drop_style == "SCENARIO":
                self.is_scenario_drop = True
                self.drop_emoji = f"🎞️"
            elif self.drop_style == "SKIN":
                self.is_skin_drop = True
                self.drop_emoji = f"✨"
            elif self.drop_style == "BOSS":
                self.is_boss_drop = True
                self.drop_emoji = f"👹"
            elif self.drop_style == "DESTINY":
                self.is_destiny_drop = True
                self.drop_emoji = f"✨"

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
            self._tactician_points = 0
            self._tactician_block = False
            self._tactician_stack_1 = False
            self._tactician_stack_2 = False
            self._tactician_stack_3 = False
            self._tactician_stack_4 = False
            self._tactician_stack_5 = False
            self._tactical_strike_used = False
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
            self.philosopher_stone = False
            if self.universe == "Full Metal Alchemist":
                self.philosopher_stone = True
            self.equivalent_exchange = 0
            self._final_stand = False
            if self.universe == "Dragon Ball Z":
                self._final_stand =True
            self._chainsawman_activated = False
            self._chainsawman_revive_active = False
            if self.universe == "Chainsawman":
                self._chainsawman_activated = True
                self._chainsawman_revive_active = True
            self._atk_chainsawman_buff = False
            self._def_chainsawman_buff = False
            self._first_offering = False
            self.devils_endurance_timer = 3
            self.devils_endurance_active = False
            self.contract_buff = 0
            self._demon_slayer_buff = 0
            self._demon_slayer_crit = False
            self._blood_demon_art = False
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
            self.fairy_tail_recovering = False
            self.fairy_tail_recovering_duration = 0
            self.souls_phase = False
            self.overlord_fear_bool = False
            self.overlord_fear_duration = 0
            self.overlord_opponent_original_defense = 0
            self.jujutsu_kaisen_focus_crit_used = False
            self.jujutsu_kaisen_domain_expansion_active = False
            self.jujutsu_kaisen_opponent_resolved_before_self = False
            self.jujutsu_kaisen_damage_check_turn_count = 0
            self.jujutsu_kaisen_damage_meter = 0
            # This is how much damage will be dealt to you under the second phase of the domain expansion trait
            self.jujutsu_kaisen_damage_meter_max = 0
            self.bleach_first_release_used = False
            self.bleach_first_release_shikai = False
            self.bleach_first_release_vollstandig = False
            self.bleach_first_release_fullbring_activation = False
            self.bleach_first_release_resurreccion = False
            self.bleach_second_release_used = False
            self.bleach_second_release_bankai = False
            self.bleach_second_release_segunda_etapa = False
            self.bleach_second_release_segunda_etapa_activated = False
            self.bleach_second_release_fullbring_completion = False
            self.bleach_second_release_schrift = False
            self.bleach_quincy_ap_buff = 0
            self.bleach_hollow_ap_buff = 0
            self.bleach_fullbring_ap_buff = 0
            self.titan_bonus = 0
            self.omingear_bonus = 0
            self.soul_resonance = False
            self.soul_resonance_amount = 0
            


            self.slime_buff = 0
            self.universe_trait_value = 0
            self.universe_trait_value_name = ""
            if self.universe == "Naruto":
                self.universe_trait_value_name = "Hashirama Cells"
            if self.universe == "Full Metal Alchemist":
                self.universe_trait_value_name = "Equivalent Exchange"
            if self.universe == "My Hero Academia":
                self.universe_trait_value_name = "Quirk Energy"
            if self.universe == "Chainsawman":
                self.universe_trait_value_name = "Contract Offering"
            if self.universe == "Jujustu Kaisen":
                self.universe_trait_value_name = "Domain Expansion"
            if self.universe == "Attack On Titan":
                self.universe_trait_value_name = f"Titan Fortitude: {self.titan_bonus}\n{self.universe_crest}Omnigear Velocity"
            if self.universe == "Soul Eater":
                self.universe_trait_value_name = "Souls"


            # Elemental Effect Meters
            self.burn_dmg = 0
            self.poison_dmg = 0
            self.rot_dmg = 0
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
            self.sword_crit = False

            self.water_buff_by_value = 100
            self.time_buff_by_value = 4
            self.earth_buff_by_value = .25
            self.death_buff_by_value = .25
            self.light_buff_by_value = .25
            self.light_speed_attack_value = 0
            self.dark_buff_by_value = 15
            self.physical_parry_value = 1
            self.ranged_buff_value = 2
            self.life_buff_value = .40
            self.reckless_buff_value = .40
            self.reckless_duration = 0
            self.reckless_rest = False
            self.psychic_barrier_buff_value = 1
            self.psychic_debuff_value = .10
            self.fire_buff_value = .50
            self.electric_buff_value = .10
            self.poison_damage_value = .35
            self.rot_damage_value = .15
            self.gravity_debuff_value = .25
            self.bleed_hit_value = 10
            self.ice_duration = 0
            self.ice_buff_value = 1
            self.energy_buff_value = 0
            self.energy_crit_bool =False
            self.wind_buff_value = .50
            self.nature_buff_value = .25
            self.sword_crit_bool = False
            self.sword_crit_count = 0
            self.sword_atk_buff_value = .40
            self.nature_debuff_value = .25
            self.sleep_counter = 0
            self.sleep_rest_skips = 0
            self.sleep_exhaustion_bool = False

            #Title Checks For Damage
            self.title_blitz = False #parry
            self.title_strategist = False #all
            self.title_pierce = False #barrier
            self.title_obliterate = False #shield
            

            # Card Defense From Arm
            # Arm Help
            self.shield_active = False
            self.barrier_active = False
            self.parry_active = False
            self.siphon_active = False

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
            self.used_blitz = False
            self.blitz_buff = 0
            self.blitz_count = 0 
            self.focus_count = 0
            self.ai_focus_message_sent = False
            self.damage_received = 0
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
            # self.class_message = self.card_class.title()
            self.class_emoji = crown_utilities.class_emojis[self.card_class]
            self.level_icon = "🔰"
            self.class_tier = ""
            self.class_level = crown_utilities.get_class_value(self.tier)
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
            elif self.tier in [8, 9]:
                self.class_tier = "Mythical"
                if self.universe == "Fate":
                    self.class_tier = "Apex"
            # elif self.tier in [9]:
            #     self.class_tier = "Apex"
            #     if self.universe == "Fate":
            #         self.class_tier = "God"
            elif self.tier in [10]:
                self.class_tier = "God"
                if self.universe == "Fate":
                    self.class_tier = "Creator God"
            
            self.class_message = f"{self.card_class.title()}"
            if self.tier > 3:
                self.class_message = f"{self.class_tier} {self.card_class.title()}"
            self.class_value = 0


            # Talisman Info
            self._talisman = "None"

            # Summon Info
            self.summon_ability_name = ""
            self.summon_power = 0
            self.base_summon_power = 0
            self.summon_lvl = 0
            self.summon_type = ""
            self.summon_bond = 0
            self.summon_name = ""
            self.summon_image = ""
            self.summon_universe = ""
            self.summon_bondexp = 0
            self.summon_exp = 0
            self.summon_emoji = ""

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
            self.move1_damage_dealt = 0
            
            #Souls Third Phase 
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
            self.move2_damage_dealt = 0
            

            # Move 3
            self.move3 = list(self.m3.keys())[0]
            self.move3ap = list(self.m3.values())[0] + self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff
            self.move3_stamina = list(self.m3.values())[1]
            self.move3_element = list(self.m3.values())[2]
            self.move3_emoji = crown_utilities.set_emoji(self.move3_element)
            self.move3base = self.move3ap
            self.move3_damage_dealt = 0

            # Move Enhancer
            self.move4 = list(self.enhancer.keys())[0]
            self.move4_stamina = list(self.enhancer.values())[1]
            self.move4enh = list(self.enhancer.values())[2]
            self.move4ap = list(self.enhancer.values())[0]
            self.move4base = self.move4ap
            self.move4enh_suffix = crown_utilities.enhancer_suffix_mapping[self.move4enh]
            self.enh_short_name = self.move4enh
            if self.move4enh in ['HLT','DESTRUCTION','CREATION']:
                if self.move4enh == 'HLT':
                    self.enh_short_name = 'HEAL'
                if self.move4enh == 'DESTRUCTION':
                    self.enh_short_name = 'DESTROY'
                if self.move4enh == 'CREATION':
                    self.enh_short_name = 'CREATE'

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
            self.trait_message = ""
            self.universe_buff_message = " "

            self.universe_image = ""
            self.tip = ""
            self.view_card_message = ""
            
            self.index = ""
            self.enhancer_values = {
                "ATK": {1: 10, 2: 15, 3: 20, 4: 30, 5: 40, 6: 50, 7: 60, 8: 70, 9: 80, 10: 90},
                "DEF": {1: 10, 2: 15, 3: 20, 4: 30, 5: 40, 6: 50, 7: 60, 8: 70, 9: 80, 10: 90},
                "HLT": {1: 10, 2: 15, 3: 20, 4: 30, 5: 40, 6: 50, 7: 60, 8: 70, 9: 80, 10: 90},
                "FLOG": {1: 10, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 40, 8: 45, 9: 50, 10: 60},
                "WITHER": {1: 10, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 40, 8: 45, 9: 50, 10: 60},
                "LIFE": {1: 10, 2: 15, 3: 20, 4: 30, 5: 40, 6: 50, 7: 60, 8: 70, 9: 80, 10: 90},
                "BZRK": {1: 10, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 40, 8: 45, 9: 50, 10: 55},
                "BRACE": {1: 10, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 40, 8: 45, 9: 50, 10: 55},
                "RAGE": {1: 10, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 40, 8: 45, 9: 50, 10: 55},
                "CRYSTAL": {1: 10, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 40, 8: 45, 9: 50, 10: 55},
                "STAM": {1: 10, 2: 15, 3: 20, 4: 30, 5: 40, 6: 60, 7: 80, 8: 100, 9: 130, 10: 160},
                "DRAIN": {1: 5, 2: 10, 3: 15, 4: 20, 5: 25, 6: 30, 7: 35, 8: 40, 9: 45, 10: 50},
                "SLOW": {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 3, 8: 4, 9: 4, 10: 5},
                "HASTE": {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 3, 8: 4, 9: 4, 10: 5},
                "CREATION": {1: 200, 2: 400, 3: 600, 4: 800, 5: 1000, 6: 1200, 7: 1400, 8: 1600, 9: 1800, 10: 2000},
                "WAVE": {1: 200, 2: 250, 3: 300, 4: 400, 5: 500, 6: 750, 7: 900, 8: 1000, 9: 1250, 10: 1500},
                "STANCE": {1: 50, 2: 75, 3: 150, 4: 200, 5: 250, 6: 300, 7: 350, 8: 400, 9: 450, 10: 500},
                "CONFUSE": {1: 50, 2: 75, 3: 150, 4: 200, 5: 250, 6: 300, 7: 350, 8: 400, 9: 450, 10: 500},
                "DESTRUCTION": {1: 5, 2: 10, 3: 15, 4: 25, 5: 30, 6: 50, 7: 75, 8: 100, 9: 150, 10: 200},
                "FEAR": {1: 50, 2: 75, 3: 100, 4: 150, 5: 200, 6: 250, 7: 300, 8: 400, 9: 450, 10: 500},
                "GROWTH": {1: 50, 2: 75, 3: 100, 4: 150, 5: 200, 6: 250, 7: 300, 8: 400, 9: 450, 10: 500},
                "GAMBLE": {1: 800, 2: 1000, 3: 1200, 4: 1500, 5: 2000, 6: 2500, 7: 3000, 8: 4300, 9: 5000, 10: 6500},
                "SOULCHAIN": {1: 50, 2: 70, 3: 90, 4: 120, 5: 140, 6: 160, 7: 180, 8: 200, 9: 220, 10: 240},
                "BLAST": {1: 10, 2: 15, 3: 20, 4: 50, 5: 75, 6: 100, 7: 150, 8: 250, 9: 350, 10: 450},
            }

            self.ai_encounter_message = ""
            self.ai_start_encounter_message = ""
            


        def set_enhancer_value(self):
            if self.move4enh in self.enhancer_values:
                set_of_values = self.enhancer_values[self.move4enh]
                self.move4ap = set_of_values.get(self.tier, 0)  # Default to 0 if tier is not found
                self.move4base = self.move4ap
                        
                 
        def set_drop_style(self):
            if self.drop_style == "TALES":
                self.is_tale_drop = True
                self.drop_emoji = f"🎴"
            elif self.drop_style == "DUNGEON":
                self.is_dungeon_drop = True
                self.drop_emoji = f"🔥"
            elif self.drop_style == "RAID":
                self.is_raid_drop = True
                self.drop_emoji = f"💀"
            elif self.drop_style == "SCENARIO":
                self.is_scenario_drop = True
                self.drop_emoji = f"🎞️"
            elif self.drop_style == "SKIN":
                self.is_skin_drop = True
                self.drop_emoji = f"✨"
            elif self.drop_style == "BOSS":
                self.is_boss_drop = True
                self.drop_emoji = f"👹"
            elif self.drop_style == "DESTINY":
                self.is_destiny_drop = True
                self.drop_style = f"✨"


        def set_battle_menu_affinity_message(self):
            try:
                def build_message(attr, label):
                    attr_list = [crown_utilities.set_emoji(a) for a in attr if a]
                    return f"{label}: {' '.join(attr_list)}" if attr_list else ""

                attributes = {
                    'Weaknesses': self.weaknesses,
                    'Resistances': self.resistances,
                    'Repels': self.repels,
                    'Absorbs': self.absorbs,
                    'Immunity': self.immunity
                }

                message_list = [build_message(attr, label) for label, attr in attributes.items() if build_message(attr, label)]
                self.affinity_message = "\n".join(message_list) if message_list else "No Affinities"

                return self.affinity_message

            except Exception as ex:
                custom_logging.debug(ex)


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
                    if weakness and weakness != "N/A":
                        emoji = crown_utilities.set_emoji(weakness)
                        weakness_list.append(emoji)

                for resistance in self.resistances:
                    if resistance and resistance != "N/A":
                        emoji = crown_utilities.set_emoji(resistance)
                        resistance_list.append(emoji)

                for repel in self.repels:
                    if repel and repel != "N/A":
                        emoji = crown_utilities.set_emoji(repel)
                        repels_list.append(emoji)

                for absorb in self.absorbs:
                    if absorb and absorb != "N/A":
                        emoji = crown_utilities.set_emoji(absorb)
                        absorb_list.append(emoji)

                for immune in self.immunity:
                    if immune and immune != "N/A":
                        emoji = crown_utilities.set_emoji(immune)
                        immune_list.append(emoji)

                if weakness_list and "N/A" not in weakness_list:
                    weakness_msg = " ".join(weakness_list)
                    message_list.append(f"**Weaknesses:** {weakness_msg}")
                
                if resistance_list and "N/A" not in resistance_list:
                    resistances_msg = " ".join(resistance_list)
                    message_list.append(f"**Resistances:** {resistances_msg}")
                
                if repels_list and "N/A" not in repels_list:
                    repels_msg = " ".join(repels_list)
                    message_list.append(f"**Repels:** {repels_msg}")

                if absorb_list and "N/A" not in absorb_list:
                    absorb_msg = " ".join(absorb_list)
                    message_list.append(f"**Absorbs:** {absorb_msg}")

                if immune_list and "N/A" not in immune_list:
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
                custom_logging.debug(ex)


        def set_universe_image(self):
            self.universe_image = db.queryUniverse({'TITLE': self.universe})['PATH']
            return self.universe_image


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


    except Exception as ex:
        custom_logging.debug(ex)


    def is_universe_unbound(self):
        if(self.universe == "Unbound"):
            return True


    def set_card_level_icon(self, player):
        for card in player.card_levels:
            if self.name == card['CARD']:
                self.card_lvl = int(card['LVL'])
        if self.card_lvl >= 200:
            self.level_icon = "🔱"
        if self.card_lvl >= 700:
            self.level_icon ="⚜️"
        if self.card_lvl >=999:
            self.level_icon ="🏅"


    def set_class_buffs(self):
        value = 0
        p_value = 0
        mage_buff = .35
        heal_buff = .30
        if self.tier in [1, 2, 3]:
            value = 2
            p_value = 3
        elif self.tier in [4, 5]:
            value = 3
            p_value = 4
            mage_buff = .45
            heal_buff = .40
            self.class_tier = "Elite"
            if self.universe == "Fate":
                self.class_tier = "Legendary"
        elif self.tier in [6, 7]:
            value = 4
            p_value = 5
            mage_buff = .50
            heal_buff = .50
            self.class_tier = "Legendary"
            if self.universe == "Fate":
                self.class_tier = "Mythical"
        elif self.tier in [8, 9]:
            value = 5
            p_value = 6
            mage_buff = .55
            heal_buff = .60
            self.class_tier = "Mythical"
            if self.universe == "Fate":
                self.class_tier = "Apex"
        elif self.tier in [10]:
            value = 6
            p_value = 7
            mage_buff = .60
            heal_buff = .70
            self.class_tier = "God"
            if self.universe == "Fate":
                self.class_tier = "Creator God"
        self.class_value = value
        self.p_value = p_value
        self.class_message = f"{self.card_class.title()}"
        if self.tier > 3:
            self.class_message = f"{self.class_tier} {self.card_class.title()}"
        
        if self.card_class == "FIGHTER":
            self.is_fighter = True
            self.parry_active = True
            self._parry_value = self._parry_value + p_value
            self.physical_parry_value = 1
            self.class_value = p_value
            self.class_tutorial_message = f"🔄 +{p_value} Parries!"
            self.fighter_bonus = 0 
        
        if self.card_class == "MAGE":
            self.is_mage = True
            self._magic_active = True
            self._magic_value = mage_buff
            self.water_buff_by_value = 200
            self.time_buff_by_value = 8
            self.earth_buff_by_value = .50
            self.death_buff_by_value = .50
            self.light_buff_by_value = .50
            self.dark_buff_by_value = 20
            self.life_buff_value = .60
            self.psychic_barrier_buff_value = 2
            self.psychic_debuff_value = .25
            self.fire_buff_value = .75
            self.electric_buff_value = .25
            self.poison_damage_value = .50
            self.rot_damage_value = .30
            self.gravity_debuff_value = .50
            self.bleed_hit_value = 30
            self.ice_buff_value = 2
            self.energy_buff_value = 2
            self.wind_buff_value = 75
            self.nature_buff_value = .50
            self.class_value = round(mage_buff * 100)
            self.class_tutorial_message = f"🔅 +{self.class_value}% Elemental Damage!"
        
        if self.card_class == "TACTICIAN":
            self.is_tactician = True
            self.class_tutorial_message = f"Craftable Protections\n🔄+{p_value - 2} Parries\n🌐+{(self.tier * 100)} Shield\n💠+{(self.class_value - 1)} Barrier"

        if self.card_class == "RANGER":
            self.is_ranger = True
            self.barrier_active = True
            self._barrier_value = self._barrier_value + value
            self.ranged_buff_value = 4
            self.class_tutorial_message = f"💠+{value} Barrier!"
            
        
        if self.card_class == "TANK":
            self.is_tank = True
            self.shield_active = True
            self._shield_value = self._shield_value + (self.tier * 250) + self.card_lvl
            self.class_value = self._shield_value
            self.class_tutorial_message = f"🌐 +{(self.tier * 250) + self.card_lvl} Shield!"
        
        if self.card_class == "HEALER":
            self.is_healer = True
            self._heal_active = True
            self._heal_value = 0
            self._heal_buff = heal_buff
            self.life_buff_value = .50
            self.class_value = round(heal_buff * 100)
            self.class_tutorial_message = f"❤️‍🩹 +{self.class_value}% Healing!"
        
        if self.card_class == "ASSASSIN":
            self.is_assassin = True
            self._assassin_active = True
            self._assassin_attack = value
            self.class_tutorial_message = f"{self.class_emoji} +{value} Sneak Attacks!"
            
        if self.card_class == "SWORDSMAN":
            self.is_swordsman = True
            self._swordsman_active = True
            self._swordsman_value = value
            self.bleed_hit_value = 20
            self.sword_atk_buff_value = .50
            self.class_tutorial_message = f"{self.class_emoji} +{value} Critical Strikes!"
            
        if self.card_class == "SUMMONER":
            self.is_summoner = True
            self._summoner_active = True
            
        if self.card_class == "MONSTROSITY":
            self.is_monstrosity = True
            self._monstrosity_active = True
            self._monstrosity_value = value - 1
            self.class_tutorial_message = f"{self.class_emoji} +{(self._monstrosity_value)} Double Strikes!"


    # AI ONLY BUFFS
    def set_ai_card_buffs(self, ai_lvl_buff, ai_stat_buff, ai_stat_debuff, ai_health_buff, ai_health_debuff, ai_ap_buff, ai_ap_debuff, prestige_level, rebirth_level, mode):
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
        self.set_class_buffs()

        
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
                return 900
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
        elif mode == "DuoTales":
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
        elif mode == "CoopTales":
            if card_lvl >= 285:
                return 300
            else:
                return card_lvl + 15
        elif mode == "CoopDungeon":
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
            

            if list_of_card_levels:
                for x in list_of_card_levels:
                    if x.get('CARD') == self.name:
                        self.card_lvl = x.get('LVL', 0)
                        self.card_exp = x.get('EXP', 0)
                        self.card_tier = x.get('TIER', self.tier)
                        self.tier = x.get('TIER', self.tier)
                        self.card_class = x.get('CLASS', self.card_class)
                        self.card_id = x.get('ID', self.card_id)
                        break

            
            self.set_class_buffs()

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
            if self.move3_element == "DRACONIC":
                self.move3ap = self.move1ap + self.move2ap

            self.set_enhancer_value()
            if self.summon_type in ['BARRIER', 'PARRY']:
                if self.summon_bond >= 1 and self.summon_lvl >= 1:
                    self.summon_power = self.summon_power + 1
            else:
                self.summon_power = round((int(self.summon_bond + 1) * int(self.summon_lvl + 1)) +  ((1 + self.summon_bond) * int(self.summon_power)))
                if self.summon_type == "DRACONIC":
                    self.summon_power = self.move1ap + self.move2ap
        except Exception as ex:
            custom_logging.debug(ex)
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

        except Exception as ex:
            custom_logging.debug(ex)
            return False  
    

    def set_tip_and_view_card_message(self):
        has_scenario = db.queryScenario({"DESTINY_CARDS": self.name})

        if self.is_skin_drop:
            self.view_card_message = f"{self.name} is a card Skin. "
            self.tip = f"Earn the {self.skin_for} card and use gems to /craft this Skin!"
        
        if self.is_destiny_drop:
            self.view_card_message = f"{self.name} is a Destiny card. "
            # self.tip = f"Complete {self.universe} Destiny: {self.collection} to unlock this card."
            self.tip = f"Complete the proper {self.universe} Destiny to unlock this card."
        
        if self.is_dungeon_drop:
            self.view_card_message = f"{self.name} is a Dungeon card. "
            self.tip = f"/craft or Find this card in the {self.universe} Dungeon"
        
        if self.is_boss_drop:
            self.view_card_message = f"{self.name} is a Boss card."
            self.tip = f"Defeat {self.universe} Boss to earn this card."
        
        if self.attack > self.defense:
            self.view_card_message = f"{self.name} is an offensive card. "
            self.tip = f"Tip: Equipping {self.universe} /titles and defensive /arms would help boost survivability"
        
        if self.defense > self.attack:
            self.view_card_message = f"{self.name} is a defensive card. "
            self.tip = f"Tip: Equipping {self.universe} /titles and offensive /arms would help boost killability"
        else:
            self.view_card_message = f"{self.name} is a balanced card. "
            self.tip = f"Tip: Equip {self.universe} /titles and /arms that will maximize your Enhancer"

        if has_scenario:
            self.tip = f"This card has 🌟 Destiny battles available in Scenarios. To access, just type /play and select scenarios in the {self.universe.capitalize()} universe."

    
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
                self.attack += arm_value
                self.defense += arm_value

            if arm_type == "SHIELD":
                self.shield_active = True
                self._shield_value = self._shield_value + arm_value
                if self.is_fighter:
                    self._shield_value = self._shield_value * 2

            if arm_type == "BARRIER":
                self.barrier_active = True
                self._barrier_value = self._barrier_value + arm_value
                if self.is_fighter:
                    self._barrier_value = self._barrier_value

            if arm_type == "PARRY":
                self.parry_active = True
                self._parry_value = self._parry_value + arm_value

            if arm_type == "SIPHON":
                self.siphon_active = True
                self._siphon_value = self._siphon_value + arm_value

            if arm_type == "MANA":
                self.move1ap = round(self.move1ap * (arm_value / 100))
                self.move2ap = round(self.move2ap * (arm_value / 100))
                self.move3ap = round(self.move3ap * (arm_value / 100))
                self.move4ap = round(self.move4ap * (arm_value / 100))

        except Exception as ex:
            custom_logging.debug(ex)
            return False


    def set_universal_buffs(self, arm_universe, title_universe):
        if (arm_universe == self.universe) and (title_universe == self.universe):
            self.attack += 100 + round(self.attack * (.05 * self.class_level))
            self.defense += 100 + round(self.defense * (.05 * self.class_level))
            self.health += 100 + round (self.health * (.05 * self.class_level))    
            self.max_health += 100 + round (self.max_health * (.05 * self.class_level))
            self.universe_buff_message = "__Universe Buff Applied__"
            if self.drop_style == "DESTINY":
                self.attack += 500 + round(self.attack * (.05 * self.tier))
                self.defense += 500 + round(self.defense * (.05 * self.tier))
                self.health += 500 + round (self.health * (.05 * self.tier))
                self.max_health += 500 + round (self.max_health * (.05 * self.tier))
                self.universe_buff_message = "__Destiny Buff Applied__"


    def set_explore_bounty_and_difficulty(self, battle_config, map_level=0):
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
        if self.tier == 8:
            self.bounty = random.randint(400000, 500000)
        if self.tier == 9:
            self.bounty = random.randint(600000, 700000)
        if self.tier == 10:
            self.bounty = random.randint(800000, 1000000)

        mode_selector_randomizer = random.randint(0, 500)


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
            self.bounty = self.bounty * 2

        if mode_selector_randomizer <= 69 and mode_selector_randomizer >= 20:
            selected_mode = "Hard"
            self.approach_message = "🔥 An Empowered "
            self._explore_cardtitle = {'TITLE': 'Dungeon Title'}
            self.card_lvl = random.randint(500, 999)
            self.bounty = self.bounty * 5


        if mode_selector_randomizer <= 19:
            selected_mode = "Impossible"
            self.approach_message = "👹 An Impossible "
            self._explore_cardtitle = {'TITLE': 'Dungeon Title'}
            self.card_lvl = random.randint(850, 1500)
            self.bounty = self.bounty * 10

        if self.tier == 7:
            self.card_lvl = random.randint(1000, 1800)
        if self.tier == 6:
            self.card_lvl = random.randint(900, 1500)

        if battle_config.is_rpg:
            selected_mode = "RPG"
            self.approach_message = "🗺️ Encounter with "
            self._explore_cardtitle = {'TITLE': 'Universe Title'}
            high, low = crown_utilities.set_opponent_level_ranges(map_level)
            if battle_config.is_hard_difficulty:
                low = low * 2
                high = high * 2

            self.card_lvl = random.randint(low, high)
            self.bounty = self.bounty * 2

        if battle_config.is_hard_difficulty:
            self.attack = self.attack + (100 *self.tier)
            self.defense = self.defense + (100 * self.tier)
            self.max_health = self.max_health + (100 * self.tier)
            self.health = self.health + (500 * self.tier)
            random_mod = random.randint(0,1000000)
            self.bounty = self.bounty + (100000 * self.tier) + random_mod

        if self.bounty >= 150000:
            bounty_icon = "💸"
        elif self.bounty >= 100000:
            bounty_icon = "💰"
        elif self.bounty >= 50000 or self.bounty <= 49999:
            bounty_icon = "💵"



        self.card_lvl_attack_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_defense_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_ap_buff = crown_utilities.level_sync_stats(self.card_lvl, "AP")
        self.card_lvl_hlt_buff = crown_utilities.level_sync_stats(self.card_lvl, "HLT")



        self.bounty_message = f"{bounty_icon} {'{:,}'.format(self.bounty)}"
        self.battle_message = "\n:crown: | **Glory**: Earn the Card & 2x Bounty, If you Lose, You lose gold!\n🪙 | **Gold**: Earn gold only!"
        if battle_config.is_rpg:
            self.battle_message = f"💬Talk to interact with {self.name}...\n🆚Fight to battle, win and this card and rewards!"
        self.set_card_level_buffs(None)


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
            turn_total = turn_total - 1
            bleed_hit_local = self.bleed_hit_value * turn_total
            bleed_hit_modified = bleed_hit_local + (self.health * .05)
            self.health = self.health - bleed_hit_modified
            if self.health < 0:
                self.health = 0
            self.damage_received = self.damage_received + round(bleed_hit_modified)
            opponent_card.damage_dealt = opponent_card.damage_dealt + round(bleed_hit_modified)
            return f"({turn_total}) 🅱️ {opponent_card.name} shredded {self.name} for {round(bleed_hit_modified):,} bleed damage"


    def set_burn_hit(self, opponent_card, turn_total):
        burn_message = None
        if opponent_card.burn_dmg > 15:
            turn_total = turn_total - 1
            if turn_total < 0:
                turn_total = 0
            self.health = self.health - opponent_card.burn_dmg
            burn_message =  f"({turn_total}) 🔥 {self.name} was burned for {round(opponent_card.burn_dmg):,} damage"
            self.damage_received = self.damage_received + round(opponent_card.burn_dmg)
            opponent_card.damage_dealt = opponent_card.damage_dealt + round(opponent_card.burn_dmg)
            if self.health <= 0:
                burn_message = f"({turn_total}) 🔥 {self.name} burned for {round(opponent_card.burn_dmg):,} damage and died"
                self.health = 0
                opponent_card.burn_dmg = 0

        opponent_card.burn_dmg = round(opponent_card.burn_dmg / 1.5)


        if opponent_card.burn_dmg <= 14 and self.health > 0:
            opponent_card.burn_dmg = 0
            burn_message = None
        return burn_message


    def frozen(self, battle_config, opponent_card):
        if opponent_card.freeze_enh:
            battle_config.next_turn()
        return {"MESSAGE" : f"({battle_config.turn_total}) ❄️ {self.name} is frozen for {opponent_card.ice_duration} turn", "TURN": battle_config.is_turn}


    def reckless_recovery(self, battle_config):
        if self.reckless_rest:
            if self.reckless_duration > 0:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🛌 {self.name} is recovering for {self.reckless_duration} more turns")
                battle_config.next_turn()
            if self.reckless_duration == 0:
                self.reckless_rest = False
                self.reckless_duration = 0
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🛌 {self.name} has recovered from Reckless Rest")
            self.reckless_duration = self.reckless_duration - 1
        return 
    

    def sword_crit_strike(self, element, battle_config):
        crit_this_turn = False
        if element == "SWORD":
            if self.sword_crit:
                self.sword_crit = False
                self.attack = self.attack + (self.attack * self.sword_atk_buff_value)
                self.sword_crit_count = 0
                crit_this_turn = True
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ⚔️ {self.name} has activated Sword Crit Strike")
                return 20

            if not self.sword_crit and not crit_this_turn:
                self.sword_crit_count = self.sword_crit_count + 1
                if self.sword_crit_count == 2:
                    self.sword_crit = True
                    self.sword_crit_count = 0
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) ⚔️ {self.name} is readying a critical strike")
                    return 0
        else:
            return 0


    def set_poison_hit(self, battle_config, opponent_card):
        if opponent_card.poison_dmg:
            self.health = self.health - opponent_card.poison_dmg
            # self.max_health = self.max_health - opponent_card.poison_dmg
            if self.health <  0 or self.max_health < 0:
                self.health = 0
            self.damage_received = self.damage_received + round(opponent_card.poison_dmg)
            opponent_card.damage_dealt = opponent_card.damage_dealt + round(opponent_card.poison_dmg)
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🧪 {self.name} was inflicted with {round(opponent_card.poison_dmg):,} poison damage")


    def set_rot_hit(self, battle_config, opponent_card):
        if opponent_card.rot_dmg:
            self.max_health = self.max_health - opponent_card.rot_dmg
            # self.max_health = self.max_health - opponent_card.poison_dmg
            if self.health <  0 or self.max_health < 0:
                self.health = 0
                self.max_health = 0
            self.damage_received = self.damage_received + round(opponent_card.rot_dmg)
            opponent_card.damage_dealt = opponent_card.damage_dealt + round(opponent_card.rot_dmg)
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩻 {self.name} was inflicted with {round(opponent_card.rot_dmg):,} rot damage to their max health")


    def set_gravity_hit(self):
        if self.gravity_hit:
            self.gravity_hit = False


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
        return self.evasion


    def set_evasion_message(self, player):
        self.get_evasion()
        self.evasion_message = f"{self.speed}"
        speed_type = "Slow"
        # Assign "Slow Speed" for speeds >= 25
        if self.speed >= 0 and self.speed <= 25:
            speed_type = "Slow Speed"

        # Assign "Average Speed" for speeds between 50 and 74 (inclusive)
        if self.speed >=26 and self.speed <= 50:
            speed_type = "Average Speed"

        # Assign "Fast Speed" for speeds between 75 and 99 (inclusive)
        if self.speed >= 51 and self.speed <= 75:
            speed_type = "Fast Speed"

        # Assign "God Speed" for speeds >= 100
        if self.speed >= 76 and self.speed <= 100:
            speed_type = "God Speed"

        if self.speed >= 70:
            if player.performance:
                self.evasion_message = f"*{speed_type}\n{round(self.evasion)}% evasion boost*"
            else:
                self.evasion_message = f"*{speed_type}\n{round(self.evasion)}% evasion boost*"
        elif self.speed <= 30:
            if player.performance:
                self.evasion_message = f"*{speed_type}\n{round(self.evasion)}% Slow*"
            else:
                self.evasion_message = f"*{speed_type}\n{round(self.evasion)}% Slow*"
        else:
            if player.performance:
                self.evasion_message = f"{speed_type}\nNo evasion boost"
            else:
                self.evasion_message = f"{speed_type}\nNo evasion boost"


        return self.evasion_message


    def showcard(self, arm="none", turn_total=0, opponent_card_defense=0, mode="non-battle", encounter=False):   
        try:    
            if self.health <= 0:
                im = get_card(self.path, self.name, "base")
                im.save("image.png")
                return interactions.File("image.png")
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

                if self.tier == 9:
                    star = Image.open("PURPLE STARS.png")

                if self.tier >= 7 and self.tier <= 8:
                    star = Image.open("RED STARS.png")
                
                if self.tier >= 4 and self.tier <= 6:
                    star = Image.open("BLUE STARS.png")

                if self.tier >= 1 and self.tier <= 3:
                    star = Image.open("STARS.png")

                if self.tier >= 10:
                    star = Image.open("DARK STARS.png")



                paste_stars(im, star, self.tier)

                name_font_size, title_font_size, basic_font_size, super_font_size, ultimate_font_size, enhancer_font_size, title_size = calculate_font_sizes(self.name, self.rname, self.used_resolve)
                universe_font_size = 35
                if self.universe == "That Time I Got Reincarnated as a Slime":
                    universe_font_size = 26
                card_message = f""
                
                # Evasion
                evasion = self.get_evasion()
                evasion_message = f"{self.speed}"
                if self.speed >= 70 or self.speed <=30:
                    evasion_message = f"{self.speed} *{self.evasion}%*"

                if arm != "none":
                    arm_message = f"{arm.passive_type.title()} | {arm.passive_value}"
                    if arm.passive_type in crown_utilities.ABILITY_ARMS:
                        arm_element_icon = crown_utilities.set_emoji(arm.element)
                        arm_message = f"🦾 {arm_element_icon} {arm.passive_type.title()}"
                        #self.element = arm.element
                    
                ebasic, especial, eultimate, engagement_basic, engagement_special, engagement_ultimate = calculate_engagement_levels(opponent_card_defense, mode, self)
                move1_text, move2_text, move3_text, move_enhanced_text, basic_font_size, super_font_size, ultimate_font_size, enhancer_font_size = calculate_move_text_and_font_sizes(self, turn_total, ebasic, especial, eultimate)

                # header = ImageFont.truetype("fonts/Yakin-MVe6w.ttf", name_font_size)

                header = ImageFont.truetype("fonts/YesevaOne-Regular.ttf", name_font_size)
                title_font = ImageFont.truetype("fonts/YesevaOne-Regular.ttf", title_font_size)
                passive_font = ImageFont.truetype("fonts/YesevaOne-Regular.ttf", universe_font_size)
                lvl_font = ImageFont.truetype("fonts/Neuton-Bold.ttf", 60)
                health_and_stamina_font = ImageFont.truetype("fonts/Neuton-Light.ttf", 41)
                attack_and_shield_font = ImageFont.truetype("fonts/Neuton-Bold.ttf", 48)
                moveset_font_1 = ImageFont.truetype("fonts/Jersey20-Regular.ttf", basic_font_size)
                moveset_font_2 = ImageFont.truetype("fonts/Jersey20-Regular.ttf", super_font_size)
                moveset_font_3 = ImageFont.truetype("fonts/Jersey20-Regular.ttf", ultimate_font_size)
                moveset_font_4 = ImageFont.truetype("fonts/Jersey20-Regular.ttf", enhancer_font_size)
                encounter_font = ImageFont.truetype("fonts/Jersey20-Regular.ttf", 33)
                

                health_bar, character_name = get_character_name_and_health_bar(self, draw, header, title_size)

                lvl_sizing = get_lvl_sizing(self, draw, lvl_font)

                # Health & Stamina
                rift_universes = ['Crown Rift Awakening']
                if self.universe in rift_universes or self.is_skin_drop or self.is_scenario_drop:
                    draw.text((710, 417), health_bar, (0, 0, 0), font=health_and_stamina_font, align="left")
                    draw.text((710, 457), f"{round(self.stamina)}", (0, 0, 0), font=health_and_stamina_font, align="left")
                else:
                    draw.text((710, 417), health_bar, (255, 255, 255), font=health_and_stamina_font, stroke_width=1,
                            stroke_fill=(0, 0, 0), align="left")
                    draw.text((710, 457), f"{round(self.stamina)}", (255, 255, 255), font=health_and_stamina_font, stroke_width=1,
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


                draw.text(a_sizing, f"{format_number(round(self.attack))}", (255, 255, 255), font=attack_and_shield_font, stroke_width=1,
                        stroke_fill=(0, 0, 0), align="center")
                draw.text(d_sizing, f"{format_number(round(self.defense))}", (255, 255, 255), font=attack_and_shield_font, stroke_width=1,
                        stroke_fill=(0, 0, 0), align="center")

                with Pilmoji(im) as pilmoji:
                    # pilmoji.text((945, 445), crown_utilities.class_emojis[self.card_class], (0, 0, 0), font=health_and_stamina_font, align="left")
                    pilmoji.text((602, 133), f"{crown_utilities.class_emojis[self.card_class]} {self.class_message}", (255, 255, 255), font=title_font, stroke_width=1, stroke_fill=(0, 0, 0),
                        align="left")
                    pilmoji.text((602, 180), f"{self.universe_crest} {self.universe}", (255, 255, 255), font=passive_font, stroke_width=1, stroke_fill=(0, 0, 0),
                        align="left")
                    if mode == "RPG" and encounter:
                        ai_encounter_message =  self.ai_encounter_message
                        wrapped_message = wrap_text(ai_encounter_message, 40)
                        pilmoji.text((602, 230), wrapped_message, (255, 255, 255), font=encounter_font, stroke_width=1, stroke_fill=(0, 0, 0), align="left")
                    else:
                        pilmoji.text((600, 250), move1_text.strip(), (255, 255, 255), font=moveset_font_1, stroke_width=2,
                                    stroke_fill=(0, 0, 0))
                        pilmoji.text((600, 290), move2_text.strip(), (255, 255, 255), font=moveset_font_2, stroke_width=2,
                                    stroke_fill=(0, 0, 0))
                        pilmoji.text((600, 330), move3_text.strip(), (255, 255, 255), font=moveset_font_3, stroke_width=2,
                                    stroke_fill=(0, 0, 0))
                        pilmoji.text((600, 370), move_enhanced_text.strip(), (255, 255, 255), font=moveset_font_4, stroke_width=2,
                                    stroke_fill=(0, 0, 0))


                image_binary = BytesIO()
                im.save(image_binary, "PNG")
                image_binary.seek(0)
                return image_binary

        except Exception as ex:
            custom_logging.debug(ex)

    async def set_ai_encounter_message(self, opponent_card, location):
        ai_encounter_message =  await ai.rpg_encounter_message(self.name, self.universe, opponent_card, location)
        self.ai_encounter_message = ai_encounter_message
        return ai_encounter_message

    async def set_ai_start_encounter_message(self, opponent_card, location):
        ai_encounter_message =  await ai.rpg_start_encounter_message(self.name, self.universe, opponent_card, location)
        self.ai_start_encounter_message = ai_encounter_message

        return ai_encounter_message
    
    def basic_attack_trait_handler(self, universe, battle_config, opponent_card):
        does_repel = False
        does_absorb = False
        self.wind_element_activated = False
        is_physical_element = False
        ranged_attack = False
        wind_buff = 0
        move_stamina = 0
        standard_traits = ['Soul Eater','Persona', 'Bleach']
        if universe == "Souls":
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

        if universe in standard_traits:
            if universe == "Soul Eater":
                self.soul_resonance = True
            move = self.move1
            ap = self.move1ap
            move_stamina = 0
            move_element = self.move1_element

            if move_element == "WIND":
                self.wind_element_activated = True
            if move_element == "RANGED" and move_stamina >= 30:
                ranged_attack = True
            if move_element == "PHYSICAL" and move_stamina >= 80:
                is_physical_element = True
            move_emoji = crown_utilities.set_emoji(move_element)

        return move, ap, move_stamina, move_element, move_emoji, self.wind_element_activated, ranged_attack, is_physical_element, does_absorb, does_repel

    
    def damage_cal(self, selected_move, battle_config, _opponent_card):
        turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

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
        move_emoji = ""
        summon_used = False
        enhancer_critical = False
        ap = 25
        ENHANCERS = [4]
        MOVES = [1,2,3,6]
        #Checking here for Souls Third Phase move
        basic_attack_traits = ['Souls','Persona', 'Bleach']
        if selected_move in basic_attack_traits:
            move, ap, move_stamina, move_element, move_emoji, self.wind_element_activated, ranged_attack, is_physical_element, does_absorb, does_repel = self.basic_attack_trait_handler(selected_move, battle_config, _opponent_card)
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
                move_emoji = crown_utilities.set_emoji(move_element)
                can_use_move_flag = True
                summon_used = True
                protections = ['BARRIER', 'SHIELD', 'PARRY']
                move = self.summon_ability_name
                move_stamina = 0

                summoner_buff = 0
                ap = self.summon_power
                true_dmg = ap
                if move_element in protections:
                    if self.is_summoner:
                        if move_element in protections:
                            summoner_buff = crown_utilities.get_class_value(self.tier)
                            ap = self.summon_power + summoner_buff

                    # Soul Eater Meister Trait
                    if self.summon_universe == "Soul Eater" and self.universe == "Soul Eater":
                        if move_element in protections:
                            ap = ap * 2

                    if move_element == "BARRIER":
                        self.barrier_active = True
                        if self._barrier_value < 0:
                            self._barrier_value = 0
                        self._barrier_value = self._barrier_value + ap
                        add_solo_leveling_temp_values(self, 'BARRIER', _opponent_card)
                        message = f"{self.summon_name} gave {self.name} a {self.summon_emoji} {ap} barrier"
                    if move_element == "SHIELD":
                        self.shield_active = True
                        if self._shield_value < 0:
                            self._shield_value = 0
                        self._shield_value = self._shield_value + ap
                        add_solo_leveling_temp_values(self, 'SHIELD', _opponent_card)
                        message = f"{self.summon_name} gave {self.name} a {self.summon_emoji} {ap} shield"
                    if move_element == "PARRY":
                        self.parry_active = True
                        if self._parry_value < 0:
                            self._parry_value = 0
                        self._parry_value = self._parry_value + ap
                        add_solo_leveling_temp_values(self, 'PARRY', _opponent_card)
                        message = f"{self.summon_name} gave {self.name} a {self.summon_emoji} {ap} parry"
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
        #set true dmg
        true_dmg = ap
        if selected_move in ENHANCERS:
            enhancer = True
            enh = self.move4enh
            ap = self.move4ap
            if random.randint(1, 20) == 20:
                ap = ap * 2
                enhancer_critical = True
            move_stamina = self.stamina if enh == "GAMBLE" else self.move4_stamina
            move = self.move4

        if (self.stamina - move_stamina) < 0:
            if not summon_used:
                can_use_move_flag = False
                response = {
                "DMG": 0, 
                "MESSAGE": "You do not have the stamina to use this move! Try another move.", 
                "CAN_USE_MOVE": can_use_move_flag, 
                "ENHANCE": False, 
                "REPEL": False, 
                "ABSORB": False, 
                "ELEMENT": move_element}
                return response

        if enhancer:
            tier = self.card_tier
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
                "GAMBLE": lambda ap: random.randint(500, ap if ap and ap >= 500 else 2500),
                "WAVE": lambda ap: ap if battle_config.is_turn == 0 else (ap if battle_config.turn_total % 10 == 0 else ap / battle_config.turn_total),
                "BLAST": lambda ap: ap if battle_config.turn_total == 0 else min(round(ap * battle_config.turn_total), 100 * self.tier),
                "CREATION": lambda ap: ap if battle_config.is_turn == 0 else (ap if battle_config.turn_total % 10 == 0 else (ap * 2 if battle_config.turn_total == round(random.randint(2, 50)) else ap / battle_config.turn_total)),
                "DESTRUCTION": lambda ap: ap if battle_config.turn_total == 0 else min(round(ap * battle_config.turn_total), 100 * self.tier), 
            }

            enhancer_value = enhancement_types.get(enh, lambda ap: 0)(ap)
            
            def get_message(move, enh, enhancer_value, tier):
                    legend = {
                        "ATK": "attack",
                        "DEF": "defense",
                        "STAM": "stamina",
                        "HLT": "health",
                        "LIFE": "health",
                        "DRAIN": "stamina",
                        "FLOG": "attack",
                        "WITHER": "defense",
                        "RAGE": "defense",
                        "BRACE": "attack",
                        "BZRK": "health",
                        "CRYSTAL": "health",
                        "RAGE_INC": "ap",
                        "BRACE_INC": "ap",
                        "BZRK_INC": "attack",
                        "CRYSTAL_INC": "defense",
                        "WAVE": "wave",
                        "BLAST": "blast"
                    }
                    if enh in ['ATK', 'DEF', 'STAM']:
                        message = f"{turn_card.name} increased their {legend[enh]} by {enhancer_value}"
                    elif enh in ['LIFE', 'DRAIN', 'FLOG', 'WITHER']:
                        if enh == 'LIFE' and enhancer_value == 0:
                            message = f"{turn_card.name} stole {enhancer_value}  of {_opponent_card.name} health."
                        else:
                            if enh == "LIFE":
                                if enhancer_value + self.health >= self.max_health:
                                    enhancer_value = round(self.max_health - self.health)
                            message = f"{turn_card.name} stole {enhancer_value} of {_opponent_card.name} {legend[enh]}!"
                    elif enh in ['RAGE', 'BRACE', 'BZRK', 'CRYSTAL']:
                        message = f"{turn_card.name} lost {enhancer_value} {legend[enh]} and gained {enhancer_value} {legend[f'{enh}_INC']}"
                    elif enh in ['WAVE', 'BLAST']:
                        if enh == 'BLAST' and enhancer_value > (150 * self.tier):
                            enhancer_value = (150 * self.tier)
                        message = f"{turn_card.name} hit {_opponent_card.name} for {round(enhancer_value)} {legend[enh]} damage"
                    elif enh in ['CREATION', 'DESTRUCTION']:
                        if enh == 'DESTRUCTION' and enhancer_value > (100 * self.tier):
                            enhancer_value = (100 * self.tier)
                        message = f"{turn_card.name} {'healed' if enh == 'CREATION' else 'destroyed'} {round(enhancer_value)} {'health and max health' if enh == 'CREATION' else f'of {_opponent_card.name} health and max health'}"
                    elif enh == 'GROWTH':
                        message = f"{turn_card.name} lost 10% max Health and increased attack, defense and ap by {round(enhancer_value)}"
                    elif enh in ['STANCE', 'CONFUSE']:
                        message = f"{turn_card.name} swapped {f'{_opponent_card.name} attack and defense' if enh == 'CONFUSE' else 'attack and defense'}, {'decreasing defense' if enh == 'CONFUSE' else 'increasing defense'} to {enhancer_value}"
                    elif enh in ['HLT']:
                        if enh == 'HLT' and enhancer_value == 0:
                            message = f"{turn_card.name} healed for {enhancer_value}"
                        else:
                            if enhancer_value + self.health >= self.max_health:
                                enhancer_value = self.max_health - self.health
                            message = f"{turn_card.name} {'healed' if enh == 'HLT' else f'sacrified 10% max health to decrease {_opponent_card.name} attack, defense and ap'} by {round(enhancer_value)}"
                    elif enh in ['FEAR']:
                        message = f"{turn_card.name} sacrified 10% max health to decrease {_opponent_card.name} attack, defense and ap by {round(enhancer_value)}"
                    elif enh in ['SOULCHAIN', 'GAMBLE']:
                        message = f"{turn_card.name} synchronized {'stamina' if enh == 'SOULCHAIN' else 'health'}  to {enhancer_value}"
                    else:
                        message = f"{turn_card.name} inflicted {enh.lower()}"
                    
                    # If enhancer is a critical hit, add a critical hit to the message
                    if enhancer_critical:
                        # add to message critical hit
                        message = f"[Critical] {message}"
                    return message
            
            m = get_message(move, enh, enhancer_value, self.tier)
            if enh in ['DRAIN', 'STAM']:
                move_stamina = 0
            
            if move_stamina != 15:
                self.stamina = self.stamina - move_stamina

            if _opponent_card.damage_check_activated:
                damage_check_message = f"[[Damage Check] {round(_opponent_card.damage_check_counter)} damage done so far]"
                battle_config.add_to_battle_log(damage_check_message)
                if _opponent_card.damage_check_counter >= _opponent_card.damage_check_limit:
                    damage_check_message = f"✅ [{self.name} passed the Damage Check]"
                    battle_config.add_to_battle_log(damage_check_message)
                    _opponent_card.damage_check_activated = False
                    _opponent_card.damage_check_counter = 0
                    _opponent_card.damage_check_limit = 0
                    _opponent_card.damage_check_turns = 0
                    _opponent_card.damage_check = False
                    _opponent_card.damage_check_turns = _opponent_card.damage_check_turns - 1
                elif _opponent_card.damage_check_turns <= 0:
                    _opponent_card.damage_check_activated = False
                    _opponent_card.damage_check_counter = 0
                    _opponent_card.damage_check_limit = 0
                    _opponent_card.damage_check_turns = 0
                    _opponent_card.damage_check = False
                    self.health = 0
                    self.defense = 0
                    self.attack = 0
                    damage_check_message = f"❌ [{self.name} failed the Damage Check]"
                battle_config.add_to_battle_log(damage_check_message)
            
            response = {"DMG": enhancer_value, "MESSAGE": m,
                        "CAN_USE_MOVE": can_use_move_flag, "ENHANCED_TYPE": enh, "ENHANCE": True, "STAMINA_USED": move_stamina, "SUMMON_USED": False}
            return response

        else:
            try:  
                #Getting the defense power of the opponent
                defensepower = _opponent_card.defense - self.attack
                # if self.sleep_exhaustion_bool:
                #     defensepower = 2000
                if defensepower <= 0:
                    defensepower = 0

                #Checking for Bonus Attack or Defense
                bonus_damage = 0
                if self.universe == "Full Metal Alchemist":
                    bonus_damage = equivalent_exchange(self, battle_config, self.attack, move_stamina)

                #Getting Attack Power of the Attacked
                attackpower = round(self.attack + ap + bonus_damage)
                if attackpower <= 0:
                    attackpower = 25

                #Getting the Ability Power
                abilitypower = attackpower - defensepower
                if abilitypower <= 0:
                    abilitypower = ap + bonus_damage

                #Engagement Checks
                dmg = abilitypower
                if dmg >= ap * 2:
                    dmg = ap * 2
                if dmg <= ap / 3:
                    dmg = ap / 3
                engagement_low = .70
                engagmement_high = .90
                if self.attack >= (_opponent_card.defense * 2):
                    engagement_low = 1.0
                    engagmement_high = 1.2
                    dmg = round(dmg * random.uniform(engagement_low, engagmement_high))
                    # print("Lethal Engagement Damage", dmg)
                elif self.attack > (_opponent_card.defense + (_opponent_card.defense * .05)):
                    engagement_low = 0.80
                    engagmement_high = 1.1
                    dmg = round(dmg * random.uniform(engagement_low, engagmement_high))
                    # print("Agrresssive Engagement Damage", dmg)
                elif self.attack < (_opponent_card.defense - (_opponent_card.defense * .05)):  
                    engagement_low = .50
                    engagmement_high = .80
                    dmg = round(dmg * random.uniform(engagement_low, engagmement_high))
                    # print("Cautious Engagement Damage", dmg)
                elif self.attack <= (_opponent_card.defense / 2):
                    engagement_low = .30
                    engagmement_high = .60
                    dmg = round(dmg * random.uniform(engagement_low, engagmement_high))
                    # print("Brave Engagement Damage", dmg)
                else:
                    dmg = round(dmg * random.uniform(engagement_low, engagmement_high))
                    # print("Neutral Engagement Damage", dmg)
                #Variance for flavor
                low = dmg - (dmg * .05)
                high = dmg + (dmg * .05)
                true_dmg = (round(random.randint(int(low), int(high))))

                #Checking for Minimum True Damage
                if true_dmg <= 0:
                    true_dmg = 50

                #Enhanced Guard Effect
                if opponent_title.enhanced_guard_effect and opponent_card.used_block:
                    battle_config.add_to_battle_log(f"(🎗️) {opponent_card.name}'s Enhanced Guard reduced {self.name}'s attack!")
                    true_dmg = true_dmg - (true_dmg * .8)

                #Naruto Chakra Control Trait
                if self.universe == "Naruto" and self.stamina >= 100:
                    true_dmg = round(true_dmg + (true_dmg * .60))
                
                #Setting Evastion Variables and Message Variable
                message = ""            
                miss_hit = 1
                low_hit = 6
                med_hit = 15
                standard_hit = 19
                high_hit = 20

                #Generate a random integer between 1 and 20 inclusive
                hit_roll = round(random.randint(1, 20))  
                
                #Evasion Modifiers
                hit_roll = self.adjust_hit_roll(battle_config, hit_roll, _opponent_card, summon_used, true_dmg, move_element, low_hit, med_hit, standard_hit, high_hit, miss_hit)
                if move_element in ["RECKLESS", "RECOIL"] and hit_roll > miss_hit:
                    if self.used_resolve:
                        true_dmg = round(true_dmg * 3)
                    else:
                        true_dmg = round(true_dmg * 2)

                if turn_title.elemental_buff_effect:
                    true_dmg = turn_title.elem_buff_handler(move_element, true_dmg)

                if opponent_title.elemental_debuff_effect:
                    true_dmg = opponent_title.elem_debuff_handler(move_element, true_dmg)

                if self._magic_active and move_element not in ['PHYSICAL', 'RANGED', 'RECKLESS', 'RECOIL', 'SWORD', 'GUN']:
                    true_dmg = round(true_dmg + (true_dmg * self._magic_value))

                if self.wind_element_activated and hit_roll < miss_hit:
                    battle_config._wind_buff = round(battle_config._wind_buff + round(true_dmg * self.wind_buff_value))
                    battle_config.add_to_battle_log(f"🌪️ All wind power increased by {round(true_dmg * self.wind_buff_value):,}")
                    true_dmg = round(true_dmg + battle_config._wind_buff)

                #Summon Ability Buffs
                summoner_buff = 0
                if summon_used and self.is_summoner:
                    summoner_buff = self.calculate_summoner_buff(true_dmg)
                    true_dmg += round(summoner_buff)

                if summon_used and self.universe == "Soul Eater":
                    hit_roll = 0

                #Set Attacker Message
                attacker = self.name
                if summon_used:
                    attacker = self.summon_name


                #Apply Hit Dice and Final Damage Modification and create message
                is_crit = False
                if hit_roll < miss_hit: #Missed Hit
                    if self.universe == 'Soul Eater':
                        is_crit = True
                        true_dmg = round(true_dmg * 2.5)
                        message = f'🩸Feint Attack! {move_emoji} {attacker} critically hit {_opponent_card.name} for {true_dmg:,} damage'
                    elif self.wind_element_activated:
                        true_dmg = round(true_dmg)
                        message = f'🌪️ {attacker} hit {_opponent_card.name} for {true_dmg:,} damage'       
                    elif turn_title.sharpshooter_effect:
                        true_dmg = round(true_dmg)
                        message = f'{move_emoji} {attacker} hit {_opponent_card.name} for {true_dmg:,} damage [🎗️Sharpshooter]'
                    else:
                        true_dmg = 0
                        message = f'{move_emoji} {attacker} attack missed {_opponent_card.name} 💨'
                
                elif hit_roll <= low_hit and hit_roll > miss_hit:#Low Hit
                    true_dmg = round(true_dmg * .70)
                    message = f'{move_emoji} {attacker} hit {_opponent_card.name} for {true_dmg:,} damage'
                
                elif hit_roll <= med_hit and hit_roll > low_hit:#Med Hit
                    true_dmg = round(true_dmg)
                    message = f'{move_emoji} {attacker} hit {_opponent_card.name} for {true_dmg:,} damage'
                
                elif hit_roll <= standard_hit and hit_roll > med_hit:#Standard Hit
                    true_dmg = round(true_dmg * 1.2)
                    message = f'{move_emoji} {attacker} hit {_opponent_card.name} for {true_dmg:,} damage'
                
                elif hit_roll >= 20:#Critical Hit
                    is_crit = True
                    if self.wind_element_activated:
                        battle_config._wind_buff = round(battle_config._wind_buff + round(true_dmg * self.wind_buff_value))
                        battle_config.add_to_battle_log(f"🌪️ All wind power increased by {round(true_dmg * self.wind_buff_value):,}")
                        true_dmg = round(true_dmg + battle_config._wind_buff)

                    if self.stagger:
                        self.stagger_activated = True
                    if self.universe =="Crown Rift Awakening":
                        true_dmg = round(true_dmg * 4)
                        message = f"🩸 {move_emoji} Blood Awakening - {attacker} critically hits {_opponent_card.name} for {true_dmg:,} damage"
                    else:
                        true_dmg = round(true_dmg * 2.5)
                        message = f"{move_emoji} {attacker} critically hits {_opponent_card.name} for {true_dmg:,} damage"
                
                else:
                    message = f"{move_emoji} {attacker} hit {_opponent_card.name} for {true_dmg:,} damage"

                if is_physical_element:
                    if self.stamina > 80:
                        true_dmg = round(true_dmg * 1.5)

                #Affinity Checks to update message
                does_repel = False
                if (move_element in _opponent_card.weaknesses or self._tactician_stack_5 ==True) and not (hit_roll <= miss_hit):
                    true_dmg = round(true_dmg * 1.6)
                    hit_type = "hit"
                    if is_crit:
                        hit_type = "Critically Hit"
                    if summon_used:
                        message = f"{move_emoji} {turn_card.summon_name} {hit_type} {_opponent_card.name} for {true_dmg:,} damage ({move_element.lower()} weakness)"
                    else:
                        message = f"{move_emoji} {turn_card.name} {hit_type} {_opponent_card.name} for {true_dmg:,} damage ({move_element.lower()} weakness)"
                
                if not self._talisman == move_element and not self._is_boss and not self._tactician_stack_3:
                    if move_element in _opponent_card.resistances and not (hit_roll <= miss_hit):
                        true_dmg = round(true_dmg * .45)
                        if summon_used:
                            message = f"{move_emoji} {turn_card.summon_name} chips {_opponent_card.name} for {true_dmg:,} damage ({move_element.lower()} resistance)"
                        else:
                            message = f"{move_emoji} {turn_card.name} chips {_opponent_card.name} for {true_dmg:,} damage ({move_element.lower()} resistance)"
                    if move_element in _opponent_card.immunity and not (hit_roll <= miss_hit):
                        true_dmg = 0
                        if summon_used:
                            message = f"{move_emoji} {turn_card.summon_name} cannot effect {_opponent_card.name} ({move_emoji} immunity)"
                        else:
                            message = f"{move_emoji} {turn_card.name} cannot effect {_opponent_card.name} ({move_emoji} immunity)"
                    if move_element in _opponent_card.repels and not (hit_roll <= miss_hit):
                        self.health = self.health - true_dmg
                        if summon_used:
                            message = f"{_opponent_card.name} repelled {turn_card.summon_name}'s attack dealing {true_dmg:,} damage ({move_emoji} repelled)"
                        else:
                            message = f"{_opponent_card.name} repelled {turn_card.name}'s attack dealing {true_dmg:,} damage ({move_emoji} repelled)"
                        does_repel = True
                        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {message}")
                    if move_element in _opponent_card.absorbs and not (hit_roll <= miss_hit):
                        _opponent_card.health = _opponent_card.health + true_dmg
                        if summon_used:
                            message = f"{_opponent_card.name} absorbed {turn_card.summon_name}'s attack for {true_dmg:,} healing ({move_emoji} absorbed)"
                        else:
                            message = f"{_opponent_card.name} absorbed {turn_card.name}'s attack for {true_dmg:,} healing ({move_emoji} absorbed)"
                        does_absorb = True
                        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {message}")
                
                #Assasin Strike Checks
                if self._assassin_active and not summon_used:
                    self._assassin_value += 1
                    self._assassin_attack = self._assassin_attack - 1
                    if self._assassin_attack >= 0:
                        strike_value = self._assassin_attack
                        battle_config.add_to_battle_log(f"(🥋) {self.name}'s sneak attack cost 0 & ignores protections [{strike_value} left]")
                    else:
                        self._assassin_active = False
                else:
                    if not self.used_block:
                        self.stamina = self.stamina - move_stamina
                #Damage Checks Checks
                if _opponent_card.damage_check_activated:
                    true_dmg = 5
                    message = f"{_opponent_card.name} is in damage check mode"

                #Healer Checks
                if _opponent_card._heal_active:
                    _opponent_card._heal_value = round(_opponent_card._heal_value + (true_dmg * _opponent_card._heal_buff))
                response = {"DMG": true_dmg, "MESSAGE": message,
                            "CAN_USE_MOVE": can_use_move_flag, "ENHANCE": False, "REPEL": does_repel, "ABSORB": does_absorb, "ELEMENT": move_element, "STAMINA_USED": move_stamina, "SUMMON_USED": summon_used}
                return response

            except Exception as ex:
                custom_logging.debug(ex)


    def adjust_hit_roll(self, battle_config, hit_roll, _opponent_card, summon_used, true_dmg, move_element, low_hit, med_hit, standard_hit, high_hit, miss_hit):
        evasion =  - 1 * crown_utilities.calculate_speed_modifier(_opponent_card.speed)
        accuracy =  -1 * crown_utilities.calculate_speed_modifier(self.speed)
        evasion_bonus = accuracy - evasion
        # print("__Evasion Checks__")
        # print("Hit Roll: ", hit_roll)
        # print("Evasion: ", evasion)
        # print("Accuracy: ", accuracy)
        # print("Evasion Bonus: ", evasion_bonus)

        hit_roll += evasion_bonus
        
        if _opponent_card.damage_check_activated:
            hit_roll += 3
            _opponent_card.damage_check_counter += true_dmg
            if not summon_used:
                _opponent_card.damage_check_turns -= 1
            if _opponent_card.damage_check_activated:
                damage_check_message = f"(🆚) [[Damage Check] {round(_opponent_card.damage_check_counter)} damage dealt so far]"
                battle_config.add_to_battle_log(damage_check_message)
                _opponent_card.damage_check_turns = _opponent_card.damage_check_turns - 1
                if _opponent_card.damage_check_counter >= _opponent_card.damage_check_limit:
                    damage_check_message = f"✅ [{self.name} passed the damage check]"
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
                    damage_check_message = f"🟥 [{self.name} failed the damage check]"
                    battle_config.add_to_battle_log(damage_check_message)

        if self.universe == "Soul Eater" and hit_roll <= low_hit:
            hit_roll = hit_roll - 3
        elif self.universe == "Soul Eater" and self.soul_resonance:
            hit_roll = 20

        #Crit tracker
        if self._demon_slayer_crit:
            hit_roll = 20
            self._demon_slayer_crit = False

        if self._swordsman_active and self.used_resolve:
                self._swordsman_value = self._swordsman_value - 1
                hit_roll = 20
                if self._swordsman_value <= 0:
                    self._swordsman_active = False
                    self._swordsman_value = 0                    
                    hit_roll = 19
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} has {self._swordsman_value} critical strikes left")


        if self.bloodlust_activated:
            hit_roll = hit_roll + 3
            self.health = self.health + (.35 * true_dmg)

        if (move_element == "ENERGY" or self.stagger or move_element == "SPIRIT") and hit_roll >= 13 and self.energy_buff_value:
            hit_roll = hit_roll + 7
            if hit_roll >= 20:
                self.energy_crit_bool = True
        
        if (move_element == "ENERGY" or self.stagger or move_element == "SPIRIT") and hit_roll >= 15 and not self.energy_buff_value:
            hit_roll = hit_roll + 5
            if hit_roll >= 20:
                self.energy_crit_bool = True

        if self.universe == "Crown Rift Awakening" and hit_roll > med_hit:
            hit_roll = hit_roll + 3
        
        if self.ranged_hit_bonus and self.is_ranger:
            hit_roll = hit_roll + self.ranged_hit_bonus

        if self.is_assassin and self._assassin_attack > 0:
            hit_roll = hit_roll + 5

        self.sword_crit_strike(move_element, battle_config)
        hit_roll = cursed_energy(self, hit_roll, battle_config)
        hit_roll = self.tactical_strike(hit_roll, battle_config)

        # This must ALWAYS stay at the bottom of the function
        if (_opponent_card.used_block or _opponent_card.used_defend) and hit_roll >= 20:
            hit_roll = 19



        return hit_roll

    def calculate_summoner_buff(self,ap):
        # Define the multipliers based on the numeric card tier
        tier_multipliers = {
            1: 0.2, 2: 0.4, 3: 0.6,
            4: 0.8, 5: 1.0,
            6: 1.2, 7: 1.4,
            8: 1.6, 9: 1.8,
            10: 2.0
        }

        # Get the multiplier for the given tier
        multiplier = tier_multipliers.get(self.tier, 0)

        # Calculate the boosted damage
        boosted_damage = round(int(ap * ( multiplier)))
        #print(boosted_damage)
        return boosted_damage


    def tactical_strike(self, current_hit_roll, battle_config):
        crit = current_hit_roll
        if self.is_tactician and self._tactician_stack_4:
            crit = current_hit_roll
            if not self._tactical_strike_used:

                crit = 20
                self._tactical_strike_used = True
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} is prepared for a tactical strike")
            return crit
        return crit


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
        if opponent_card.barrier_active:
            opponent_card._arm_message += f"{weapon_emojis['barrier']} {opponent_card._barrier_value} Barrier{'s' if opponent_card._barrier_value > 1 else ''}"
        if opponent_card.shield_active:
            opponent_card._arm_message += f"{weapon_emojis['shield']} {opponent_card._shield_value:,} Shield"
        if opponent_card.parry_active:
            opponent_card._arm_message += f"{weapon_emojis['parry']} {opponent_card._parry_value} Parr{'ies' if opponent_card._parry_value > 1 else 'y'}"
        if opponent_card.siphon_active:
            opponent_card._arm_message += f"{weapon_emojis['siphon']} {opponent_card._siphon_value} Siphon"

        if len(opponent_card._arm_message) > 0:
            opponent_card._arm_message = "\n" + opponent_card._arm_message
            

        if self.barrier_active:
            self._arm_message += f"{weapon_emojis['barrier']} {self._barrier_value} Barrier{'s' if self._barrier_value > 1 else ''}"
        if self.shield_active:
            self._arm_message += f"{weapon_emojis['shield']} {self._shield_value:,} Shield"
        if self.parry_active:
            self._arm_message += f"{weapon_emojis['parry']} {self._parry_value} Parr{'ies' if self._parry_value > 1 else 'y'}"
        if self.siphon_active:
            self._arm_message += f"{weapon_emojis['siphon']} {self._siphon_value} Siphon"

        
        if len(self._arm_message) > 0:
            self._arm_message = "\n" + self._arm_message


    async def focusing(self, _title, _opponent_title, _opponent_card, battle_config, _co_op_card=None, _co_op_title=None ):
        if self.stamina < self.stamina_required_to_focus:
            if _opponent_card.sleep_exhaustion_bool:
                _opponent_card.sleep_rest_skips = _opponent_card.sleep_rest_skips - 1

                if _opponent_card.sleep_rest_skips <= 0:
                    _opponent_card.sleep_exhaustion_bool = False
                    _opponent_card.sleep_rest_skips = 0
                    _opponent_card.sleep_counter = 0
                    sleep_message = f"({battle_config.turn_total}) {_opponent_card.name} has woken up and can now focus"
                    battle_config.add_to_battle_log(sleep_message)
                else:
                    sleep_message = f"({battle_config.turn_total}) {_opponent_card.name} is 💤 sleeping and cannot focus [{_opponent_card.sleep_rest_skips} turns to rest left]"
                    battle_config.add_to_battle_log(sleep_message)
                    battle_config.next_turn()
                    return
                    
            self.used_focus = True
            if battle_config.is_tutorial_game_mode:
                #print(battle_config.is_turn)

                if self.name == "Training Dummy" and not battle_config.tutorial_opponent_focus:
                    #print(battle_config.is_turn)
                    embedVar = battle_config.tutorial_messages(player_card=self, opponent_card=_opponent_card, message_type="OPPONENT")
                    battle_config._tutorial_message = embedVar
                if self.name != "Training Dummy" and not battle_config.tutorial_focus and not self.used_blitz:
                    embedVar = battle_config.tutorial_messages(player_card=self, opponent_card=_opponent_card, message_type='FOCUS')
                    battle_config._tutorial_message = embedVar
                
            self.usedsummon = False
            if self.used_blitz and not self.is_assassin:
                self.focus_count = self.focus_count
            else:
                self.focus_count += 1            

            if battle_config.is_boss_game_mode and battle_config.is_turn not in [1,3]:
                embedVar = interactions.Embed(title=f"{battle_config._punish_boss_description}")
                embedVar.add_field(name=f"{battle_config._arena_boss_description}", value=f"{battle_config._world_boss_description}", inline=False)
                embedVar.set_footer(text=f"{battle_config._assault_boss_description}")
                battle_config._boss_embed_message = embedVar
            elif battle_config.is_boss_game_mode and battle_config.is_turn in [1,3]:
                embedVar = interactions.Embed(title=f"{battle_config._powerup_boss_description}", color=0xe91e63)
                embedVar.add_field(name=f"A great aura starts to envelop **{self.name}** ",
                                value=f"{battle_config._aura_boss_description}")
                embedVar.set_footer(text=f"{self.name} Says: 'Now, are you ready for a real fight?'")   
                battle_config._boss_embed_message = embedVar
            
            # fortitude or luck is based on health
            fortitude = round(self.health * .1)
            if fortitude <= 50:
                fortitude = 50

            self.stamina = self.stamina_focus_recovery_amount
            health_calculation = round(fortitude)
            if self._heal_active:
                health_calculation = health_calculation + self._heal_value
                self.max_health = self.max_health + self._heal_value
                if self.health >= self.max_health:
                    self.health = self.max_health
                self._heal_value = 0
            attack_calculation = round((fortitude * (self.tier / 10)) + (.05 * self.attack))
            defense_calculation = round((fortitude * (self.tier / 10)) + (.05 * self.defense))
            
            if _title.iq_effect:
                health_calculation, attack_calculation, defense_calculation, title_message = _title.iq_handler(health_calculation, attack_calculation, defense_calculation)
            
            if _title.soulchain_effect or _opponent_title.soulchain_effect:
                health_calculation = 0
                attack_calculation = 0
                defense_calculation = 0
            
            new_health_value = 0
            heal_message = ""
            message_number = 0
            if self.used_blitz:
                heal_message = "blitzed"
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
                    heal_message = f"{_opponent_card.name}'s blows don't appear to have any effect!"
                    self.health = self.max_health
                    message_number = 0
            
            blitz_buff = round((self.speed + self.blitz_buff + self.tier) / 2)
            if not self.used_resolve or _title.high_iq_effect or self.bleach_first_release_fullbring_activation:
                armament(self, health_calculation, battle_config, attack_calculation, defense_calculation)
                
                if self.is_assassin:
                    blitz_buff += self.speed
                if not self.used_blitz:
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) (🌀) {self.name} [+❤️{health_calculation} | +🗡️ {attack_calculation} | +🛡️{defense_calculation}]")
                else:
                    attack_calculation += blitz_buff
                    defense_calculation += blitz_buff
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) (💢) {self.name} [+💢{blitz_buff} : +🗡️ {attack_calculation} | +🛡️{defense_calculation}]")
                self.attack += attack_calculation
                self.defense += defense_calculation
            
            if self.used_resolve:
                if self.used_blitz:
                    attack_calculation += blitz_buff
                    defense_calculation += blitz_buff
                    self.attack += attack_calculation
                    self.defense += defense_calculation
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) (💢) {self.name} [+💢{blitz_buff} : +🗡️ {attack_calculation} | +🛡️{defense_calculation}]")
                else:
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) (🌀) {self.name} [+❤️{health_calculation}]")

            #Check is player blitz to disable focus traits
            if not self.used_blitz:
                #Activate Elemental Stack Reductions
                if _opponent_card.poison_dmg:
                    _opponent_card.poison_dmg = round(_opponent_card.poison_dmg / 2)
                    if self.is_healer:
                        _opponent_card.poison_dmg = 0
                        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🥋 {self.name}'s Healing Aura !  ⚕️🧪 poison cured!")
                    else:
                        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name}'s 🔻🧪 poison damage reduced to {_opponent_card.poison_dmg}")

                if _opponent_card.rot_dmg:
                    _opponent_card.rot_dmg = round(_opponent_card.rot_dmg / 2)
                    if self.is_healer:
                        _opponent_card.rot_dmg = 0
                        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🥋 {self.name}'s Healing Aura !  ⚕️🩻 rot cured!")
                    else:
                        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name}'s 🔻🩻 rot damage reduced to {_opponent_card.rot_dmg}")

                if _opponent_card.burn_dmg and self.is_healer:
                    _opponent_card.burn_dmg = 0
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🥋 {self.name}'s Healing Aura ! ⚕️🔥 burn cured!")

                #Activate Focus Traits
                digivolve(self, battle_config, _opponent_card)

                turret_shot(self, battle_config, _opponent_card)

                saiyan_spirit(self, battle_config, _opponent_card)

                rulers_authority(self, battle_config, _opponent_card)

                mana_zone(self, battle_config)

                scheduled_death(self, battle_config, _opponent_card)

                rank_hero(self, battle_config, _opponent_card)

                hero_reinforcements(self, battle_config, _opponent_card)

                increase_power(self, battle_config, _opponent_card)

                combo_recognition(self, battle_config, _opponent_card)

                concentration(self, battle_config)

                fear_aura(self, _opponent_card, battle_config)

                cursed_energy_reset(self, battle_config)

                beezlebub(self, battle_config, _opponent_card)

                soul_eater(self, battle_config, _opponent_card)

                self.light_speed_attack(_opponent_card, battle_config)

            battle_config.turn_total = battle_config.turn_total + 1


            # Turned off focus messages for now
            # To make it so that only sends message 1 time, use the self.ai_focus_message_sent flag to limit
            # ai_focus_message = await ai.focus_message(self.name, self.universe, _opponent_card.name, _opponent_card.universe)
            # battle_config.add_to_battle_log(f"({battle_config.turn_total}) [{self.name}] - {ai_focus_message}")
            
            if not self.used_blitz:
                battle_config.next_turn()
            else:
                self.used_blitz = False
                battle_config.repeat_turn()


    def light_speed_attack(self, oppponent_card, battle_config):
        if oppponent_card.light_speed_attack_value:
            self.health = self.health - oppponent_card.light_speed_attack_value
            battle_config.add_to_battle_log(f"(🌕) {oppponent_card.name} used Light Speed Attack and hit {self.name} for {round(oppponent_card.light_speed_attack_value):,} light damage")
            oppponent_card.light_speed_attack_value = 0
            return


    def standard_resolve_effect(self, battle_config, opponent_card, player_title):
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

        title_message = ""

        if player_title.singularity_effect:
            resolve_health, resolve_attack_value, resolve_defense_value, title_message = player_title.singularity_handler(resolve_health, resolve_attack_value, resolve_defense_value)

        self.stamina = self.stamina + self.resolve_value
        self.health = self.health + resolve_health
        self.damage_healed = self.damage_healed + resolve_health
        self.attack = round(self.attack + resolve_attack_value)
        self.defense = round(self.defense - resolve_defense_value)
        self.used_resolve = True
        self.usedsummon = False

        lol = pentakill(self, battle_config, opponent_card)
        souls = souls_resolve(self, battle_config, resolve_health, resolve_attack_value, resolve_defense_value, title_message)
        chainsawman = contract_fulfilled(self, battle_config, resolve_health, title_message)
        soul_eater = soul_resonance(self, battle_config, resolve_health, resolve_attack_value, resolve_defense_value, title_message)
        if not any([lol, souls, chainsawman, soul_eater]):
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ⚡  {self.name} resolved {title_message} [+❤️{resolve_health} | +🗡️ {resolve_attack_value} | --🛡️{resolve_defense_value}]")

        # battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()


    async def resolving(self, battle_config, player_title, opponent_card, player=None, opponent=None):
        if self.defense <= 0:
            self.defense = 25
        if self.attack <= 0:
            self.attack = 25
        # ai_resolve_message = await ai.resolve_message(self.name, self.universe, opponent_card.name, opponent_card.universe)
        # battle_config.add_to_battle_log(f"(💬) [{self.name}] - {ai_resolve_message}")
        if not self.used_resolve and self.used_focus:

            mha_resolve = quirk_awakening(self, battle_config, player_title)

            yuyu_resolve = spirit_resolved(self, battle_config, opponent_card, player_title)

            one_piece_resolve = conquerors_haki(self, battle_config, opponent_card, player_title)

            demon_slayer_resolve = total_concentration_breathing(self, battle_config, player_title, opponent_card)

            naruto_resolve = hashirama_cells(self, battle_config, player_title)

            aot_resolve = titan_mode(self, battle_config, player_title)

            bleach_resolve = first_release(self, battle_config, player_title)
            
            gow_resolve = acension(self, battle_config, player_title)
            
            fate_resolve = command_seal(self, battle_config, opponent_card, player_title)
            
            pokemon_resolve = evolutions(self, battle_config, player_title)

            fairytail_resolve = unison_raid(self, battle_config, opponent_card, player_title)

            overlord_resolve = fear(self, battle_config, opponent_card, player_title)

            slime_resolve = skill_evolution(self, battle_config, player_title)

            fma_resolve = equivalent_exchange_resolve(self, battle_config)

            jjk_resolve = domain_expansion(self, battle_config, player_title, opponent_card)

            if not any([mha_resolve, overlord_resolve, yuyu_resolve, one_piece_resolve, demon_slayer_resolve, naruto_resolve, aot_resolve, bleach_resolve, gow_resolve, fate_resolve, pokemon_resolve, fairytail_resolve, fma_resolve]):
                self.standard_resolve_effect(battle_config, opponent_card, player_title)

            if player_title.synthesis_effect:
                self.health = self.health + player_title.synthesis_damage_stored
                player_title.synthesis_damage_stored = 0
                battle_config.add_to_battle_log(f"🎗️ [{self.name} is synthesizing, gaining {player_title.synthesis_value} health]")
            if self.overwhelming_power:
                self.parry_active = True
                self._parry_value = round(random.randint(10, 20))
                battle_config.add_to_battle_log(f"[{self.name} is overwhemlingly powerful, parrying the next {str(self._parry_value)} attacks")
            
            if battle_config.is_boss_game_mode:
                if (battle_config.is_turn == 0 or battle_config.is_turn == 2):
                    embedVar = interactions.Embed(title=f"{battle_config._rmessage_boss_description}")
                    embedVar.set_footer(text=f"{opponent_card.name} this will not be easy...")
                    battle_config._boss_embed_message = embedVar
                else:
                    embedVar = interactions.Embed(title=f"{opponent_card.name} Rebukes You!\n{battle_config._rebuke_boss_description}")
                    embedVar.set_footer(text=f"{self.name} this is your chance!")
                    battle_config._boss_embed_message = embedVar
    
            # Adjusting turn to generate arrow on summon & class messages
            # battle_config.turn_total = battle_config.turn_total + 1
            if not self.is_summoner:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🧬 {self.name} summoned {self.summon_emoji}{self.summon_name} to aid them in battle with their {self.summon_type.title()} ability")
            if self._monstrosity_active:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🥋 {self.name} gained {self._monstrosity_value} double strikes")
            if self._swordsman_active:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🥋 {self.name} gained {self._swordsman_value} critical strikes")
            if self.is_tank:
                if self._shield_value <= 0:
                    self._shield_value = 0
                self._shield_value +=  (self.tier * 250) + self.card_lvl
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🥋 {self.name} gained +🌐{(self.tier * 250) + self.card_lvl} shield")
            battle_config.turn_total = battle_config.turn_total + 1


    def usesummon(self, battle_config, opponent_card):
        if (self.used_resolve or self._summoner_active) and not (self.usedsummon or opponent_card._tactician_stack_5):
            damage_calculation_response = self.damage_cal(6, battle_config, opponent_card)
            self.usedsummon = True
            if damage_calculation_response['CAN_USE_MOVE']:
                self.damage_done(battle_config, damage_calculation_response, opponent_card)
                summon_persona(self, battle_config, opponent_card)
                summon_slime(self, battle_config, opponent_card)
                meister(self,damage_calculation_response)
                battle_config.repeat_turn()
                return damage_calculation_response
            else:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🧬 {self.summon_name} is resting")
                battle_config.repeat_turn()
        else:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🧬 {self.summon_name} is resting")
            battle_config.repeat_turn()

    
    def activate_persona_trait(self, battle_config, opponent_card):
        if self.universe == "Persona" and self.used_resolve:
            summon_response = self.usesummon(battle_config, opponent_card)
            self.activate_element_check(battle_config, summon_response, opponent_card)


    def set_talisman(self, battle_config):
        # if normal, apply talisman for basic attack
        # if hard, apply talisman for ultimate attack
        current_opponent_val = 2
        if battle_config.is_normal_difficulty:
            if battle_config.is_tales_game_mode and (battle_config.current_opponent_number < current_opponent_val):
                self._talisman = "None"
                return
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
                    battle_config.add_to_battle_log(f"(🦠) {companion_card.name} reached their full power")
            if companion_card.summon_type in ['FEAR']:
                if opponent_card.card_lvl_ap_buff <= 0:
                    battle_config.add_to_battle_log(f"(🦠) {opponent_card.name} is at minimal power")
            else:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {companion_card.name} used {companion_card.move4} to assist {self.name}")
            battle_config.turn_total = battle_config.turn_total + 1
            battle_config.next_turn()
        else:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {companion_card.name} doesn't have enough stamina to use this move")
            battle_config.repeat_turn()


    def use_block(self, battle_config, opponent_card, co_op_card=None):
        if self.stamina >= 20:
            self.used_block = True
            
            if battle_config.is_co_op_mode and not (battle_config.is_turn == 1 or battle_config.is_turn == 3):
                block_message = f"{self.name} defended 🛡️ {co_op_card.name}"
                self.used_defend = True
            else:
                block_message = f"{self.name} blocked 🛡️"
                self.used_block = True
            self.stamina = self.stamina - 20
            defense_boost = 2
            if self.card_class == "TANK":
                defense_boost = 3
            self.defense = round(self.defense * defense_boost)
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {block_message}")

            self.tactician_points(battle_config, opponent_card)
            
            shinigami_eyes(self, battle_config)
            
            rally(self, battle_config)

            grimoire(self, battle_config)

            spiritual_pressure(self, battle_config, opponent_card)

            plus_ultra(self, battle_config)

            meditation(self, battle_config)

            #Increment turn after
            battle_config.turn_total = battle_config.turn_total + 1
            battle_config.next_turn()
        else:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} is too tired to block")
            battle_config.repeat_turn()


    def tactician_points(self, battle_config, opponent_card):
        if self.is_tactician:
            if int(self.stamina) <= 0:
                #print("Activate Tactician")
                self._tactician_points = self._tactician_points + 1
                if self._tactician_points >= 5:
                    self._tactician_stack_5 = True
                    #self._double_strike_count = self._double_strike_count + 1
                    response = f"🥋 The Ultimate Strategy! {opponent_card.name}'s Summon is disabled and they weak to ALL damage! [{self._tactician_points} Strategy Points!]"
                elif self._tactician_points == 4:
                    self._tactician_stack_4 = True
                    opponent_card._tactician_stack_1 = True
                    opponent_card.parry_active = False
                    opponent_card._parry_value = 0
                    opponent_card.barrier_active = False
                    opponent_card._barrier_value = 0
                    opponent_card.shield_active = False
                    opponent_card._shield_value = 0
                    self._critical_strike_count = self._critical_strike_count + 1
                    response = f"🥋 Sabotage Protections! {self.name} gained 1 Critical Strike and destroyed {opponent_card.name}'s protections [{self._tactician_points} Strategy Points]"
                elif self._tactician_points == 3:
                    self._tactician_stack_3 = True
                    response = f"🥋 Enhance Talisman! {self.name} will bypass all  {opponent_card.name}'s affinities [{self._tactician_points} Strategy Points]"
                elif self._tactician_points == 2:
                    self._tactician_stack_2 = True
                    response = f"🥋 Sabotage Talisman! {self.name} disabled {opponent_card.name}'s {opponent_card._talisman.title()} talisman [{self._tactician_points} Strategy Points]"
                    opponent_card._talisman = "None"
                elif self._tactician_points == 1:
                    self._tactician_stack_1 = True
                    self._parry_value = self._parry_value + (self.p_value - 2)
                    if self._parry_value > 0:
                        self.parry_active = True
                    self._barrier_value = self._barrier_value + (self.class_value - 1)
                    if self._barrier_value > 0:
                        self.barrier_active = True
                    self.shield_active = True

                    if self._shield_value <= 0:
                        self._shield_value = 0
                    self._shield_value = self._shield_value + (100 * int(self.tier))
                    #print(self._shield_value)
                    response = f"🥋 {self.name} Crafted Protections!🛠️\n💠{self.class_value - 1} Barrier\n🌐{(100 * int(self.tier))} Shield\n🔁 {self.p_value - 2} Parry\n[{self._tactician_points} {self.class_tier} Strategy Points]"
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {response}")
                return 
            else:
                #print("Don't Activate Tactician")
                return False
        else:
            return False
    

    def use_defend(self, battle_config, companion_card):
        if self.stamina >= 20:
            self.used_defend = True
            self.stamina = self.stamina - 20
            self.defense = round(self.defense * 2)
            
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} defended 🛡️ {companion_card.name}")
            battle_config.turn_total = battle_config.turn_total + 1
            battle_config.next_turn()
        else:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} is too tired to block")
            battle_config.repeat_turn()
            

    def use_blitz(self, battle_config, opponent_card):
        if self.stamina <= 50 or self.is_assassin:
            self.blitz_count += 1
            self.used_blitz = True 
            self.blitz_buff = self.stamina
            self.stamina -= self.stamina

            if self.is_assassin:
                self.blitz_buff += self.speed
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} 💢 blitzed {opponent_card.name} [-🌀{self.blitz_buff} | +💢{self.blitz_buff}]")
            
            summon_blitz(self, battle_config, opponent_card)
            omnigear(self, battle_config)
            demon_slayer_blitz(self, battle_config)

            if self.is_assassin:
                if not self._assassin_active:
                    self._assassin_active = True
                if self._assassin_attack <0:
                    self._assassin_attack = 0
                self._assassin_attack += 1
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🥋 {self.name} gained +1 Sneak Attack [{self._assassin_attack}]")

            battle_config.turn_total = battle_config.turn_total + 1
            battle_config.next_turn()
        else:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} is too tired to blitz")
            battle_config.repeat_turn()
    

    def enhancer_handler(self, battle_config, dmg, opponent_card):
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
                battle_config.turn_total = battle_config.turn_total - dmg['DMG']
                if battle_config.turn_total < 0:
                    battle_config.turn_total = 0
            elif self.move4enh == 'HASTE':
                battle_config.turn_total = battle_config.turn_total +  dmg['DMG']
            elif self.move4enh == 'SOULCHAIN':
                self.stamina = round(dmg['DMG'])
                opponent_card.stamina = self.stamina
            elif self.move4enh == 'GAMBLE':
                if battle_config.is_dungeon_game_mode:
                    opponent_card.health = round(dmg['DMG']) * 3
                    self.health = round(dmg['DMG'])
                elif battle_config.is_boss_game_mode:
                    opponent_card.health = round(dmg['DMG']) * 3
                    self.health = round(dmg['DMG'])
                else:
                    opponent_card.health = round(dmg['DMG'])
                    self.health = round(dmg['DMG'])
            elif self.move4enh == 'FEAR':
                if self.universe != "Chainsawman":
                    self.max_health = round(self.max_health - (self.max_health * .10))
                    if self.health > self.max_health:
                        self.health = self.max_health

                opponent_card.defense = round(opponent_card.defense - dmg['DMG'])
                opponent_card.attack = round(opponent_card.attack - dmg['DMG'])

                # Adjusting opponent card level AP buff
                # opponent_card.card_lvl_ap_buff = max(50, round(opponent_card.card_lvl_ap_buff - dmg['DMG']))
                
                # Define a function to apply damage and ensure minimum AP/base value
                def apply_damage_and_ensure_minimum(attr, damage, min_value=50):
                    new_value = attr - damage
                    return max(min_value, new_value)

                # Apply damage to moves and ensure minimum values
                # opponent_card.move1ap = apply_damage_and_ensure_minimum(opponent_card.move1ap, dmg['DMG'])
                opponent_card.move1base = apply_damage_and_ensure_minimum(opponent_card.move1base, dmg['DMG'])
                # opponent_card.move2ap = apply_damage_and_ensure_minimum(opponent_card.move2ap, dmg['DMG'])
                opponent_card.move2base = apply_damage_and_ensure_minimum(opponent_card.move2base, dmg['DMG'])
                # opponent_card.move3ap = apply_damage_and_ensure_minimum(opponent_card.move3ap, dmg['DMG'])
                opponent_card.move3base = apply_damage_and_ensure_minimum(opponent_card.move3base, dmg['DMG'])

                # Ensure minimum value for card level AP buff
                opponent_card.card_lvl_ap_buff = max(25, opponent_card.card_lvl_ap_buff)

            elif self.move4enh == 'WAVE':
                opponent_card.health = round(opponent_card.health - dmg['DMG'])
            elif self.move4enh == 'BLAST':
                if dmg['DMG'] >= (self.tier * 100):
                    dmg['DMG'] = (self.tier * 100)
                opponent_card.health = round(opponent_card.health - dmg['DMG'])
            elif self.move4enh == 'CREATION':
                self.max_health = round(self.max_health + dmg['DMG'])
                self.health = round(self.health + dmg['DMG'])
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

            if self.move4enh in ['RAGE','BRACE','GROWTH'] and self.card_lvl_ap_buff >= 1000 + (200 * self.tier) + self.card_lvl:
                battle_config.add_to_battle_log(f"(🦠) {self.name} reached their full power")

            battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🦠 {dmg['MESSAGE']}")
            if opponent_card.jujutsu_kaisen_domain_expansion_active:
                domain_expansion_check(self, opponent_card, battle_config)
                
            if opponent_card.health <= 0:
                final_stand(self, battle_config, dmg['DMG'], opponent_card)
                devils_endurance(opponent_card, battle_config)
            else:
                battle_config.turn_total = battle_config.turn_total + 1

            return True
        else:
            return  
    
    
    def missed_attack_handler(self, battle_config, dmg, opponent_card):
        if dmg['DMG'] == 0:
            if self.barrier_active and dmg['ELEMENT'] not in ["PSYCHIC"]:
                if not dmg['SUMMON_USED'] and not self.is_ranger:
                    self.barrier_active = False
                    self._barrier_value = 0
                    self._arm_message = ""
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} disengaged their barrier to attack")
                    decrease_solo_leveling_temp_values(self, 'BARRIER', opponent_card, battle_config)
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}")
            # battle_config.turn_total = battle_config.turn_total + 1
            
            return True
        else:
            return
        
    
    def light_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "LIGHT":
            return

        if opponent_card.shield_active or opponent_card.barrier_active:
            return

        deals_damage = not opponent_card.parry_active
        if self.title_blitz or self.title_strategist:
            deals_damage = True
        light_value = round(dmg['DMG'] * self.light_buff_by_value)
        self.attack += light_value
        self.light_speed_attack_value += light_value

        if deals_damage and not draconic:
            opponent_card.health -= dmg['DMG']
            battle_log_msg = (
                f"({battle_config.turn_total}) {dmg['MESSAGE']}\n"
                f"[{self.name} gained {light_value:,} attack] [{self.light_speed_attack_value:,} 🌕 damage stored]"
            )
        else:
            battle_log_msg = (
                f"({battle_config.turn_total}) 🌕 [{self.name} gained {light_value:,} attack] "
                f"[{self.light_speed_attack_value:,} damage stored]"
            )

        battle_config.add_to_battle_log(battle_log_msg)

    
    def water_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "WATER":
            return

        if opponent_card.shield_active or opponent_card.barrier_active:
            return

        # Deals damage if not opponent_card.parry_active or not opponent_card.shield_active
        deals_damage = (not opponent_card.parry_active and not opponent_card.shield_active) 
        if (self.title_blitz or self.title_strategist or self.title_obliterate):
            deals_damage = True

        self.basic_water_buff = self.basic_water_buff + self.water_buff_by_value
        self.special_water_buff = self.special_water_buff + self.water_buff_by_value
        self.ultimate_water_buff = self.ultimate_water_buff + self.water_buff_by_value
        self.water_buff = self.water_buff + self.water_buff_by_value

        #Grant shield every 200 water buff
        water_message = f""
        if self.water_buff % 200 == 0:
            opponent_card.health -= self.water_buff
            water_message = f"| +{self.water_buff} 🌐 shield"
            self.shield_active = True
            if self._shield_value <= 0:
                self._shield_value = 0
            self._shield_value = self._shield_value + self.water_buff
        #True Damage every 400 water buff
        if self.water_buff % 400 == 0:
            opponent_card.health -= self.water_buff
            water_message = f"| {opponent_card.name} takes 💧{self.water_buff} true damage"

        if deals_damage:
            opponent_card.health -= dmg['DMG']
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}\n[💧 +{self.water_buff} AP {water_message}]")
        else:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} Increased Water Damage!\n[💧 +{self.water_buff} {water_message}]")
            

    def dark_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "DARK":
            return
        
        opponent_card.stamina = opponent_card.stamina - self.dark_buff_by_value
        opponent_card.health = opponent_card.health - dmg['DMG']
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}\n[{opponent_card.name} lost {self.dark_buff_by_value} stamina]")


    def fire_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "FIRE":
            return
        
        deals_damage = not opponent_card.parry_active
        if self.title_blitz or self.title_strategist:
            deals_damage = True
        self.burn_dmg = self.burn_dmg + round(dmg['DMG'] * self.fire_buff_value)

        if deals_damage:
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}")


    def draconic_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "DRACONIC":
            return
        
        # Get Draconic AP and Move Elements
        # Draconic Moves can ONLY be ultimate attacks
        draconic_ap = round(self.move1ap + self.move2ap)
        dmg['DMG'] = draconic_ap

        draconic_basic_element = self.move1_element
        draconic_special_element = self.move2_element

        # Splitting the Damage for Two Elemental Effects
        basic_dmg_var = dmg.copy()  # Create a copy of the dmg dictionary
        special_dmg_var = dmg.copy()  # Create a copy of the dmg dictionary
        
        total_dmg = dmg['DMG']
        split_ratio = random.uniform(0, 1)
        basic_dmg = round(total_dmg * split_ratio)
        special_dmg = total_dmg - basic_dmg  # Ensure the total always adds up

        basic_dmg_var['DMG'] = basic_dmg
        special_dmg_var['DMG'] = special_dmg
        basic_dmg_var['ELEMENT'] = draconic_basic_element
        special_dmg_var['ELEMENT'] = draconic_special_element

        
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} combined elements [{draconic_basic_element} & {draconic_special_element}]")
        self.activate_element_check(battle_config, basic_dmg_var, opponent_card)
        self.activate_element_check(battle_config, special_dmg_var, opponent_card)


    def earth_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "EARTH":
            return

        deals_damage = not opponent_card.parry_active
        if self.title_blitz or self.title_strategist:
            deals_damage = True
        self.shield_active = True

        shield_value = round(dmg['DMG'] * self.earth_buff_by_value)
        self.defense += dmg['DMG'] * self.earth_buff_by_value
        self._shield_value = max(0, self._shield_value + shield_value)
        
        add_solo_leveling_temp_values(self, 'SHIELD', opponent_card)

        if deals_damage:
            opponent_card.health -= dmg['DMG']
            battle_log_msg = (
                f"({battle_config.turn_total}) {dmg['MESSAGE']}\n"
                f"[{self.name} gained 🌐 {shield_value:,} shield]"
            )
        else:
            battle_log_msg = (
                f"({battle_config.turn_total}) "
                f"[{self.name} gained 🌐 {shield_value:,} shield]"
            )

        battle_config.add_to_battle_log(battle_log_msg)


    def death_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "DEATH":
            return

        deals_damage = not opponent_card.parry_active
        if self.title_blitz or self.title_strategist:
            deals_damage = True
        death_buff_value = round(dmg['DMG'] * self.death_buff_by_value)
        self.attack += death_buff_value
        opponent_card.max_health -= death_buff_value

        if opponent_card.health > opponent_card.max_health:
            opponent_card.health = opponent_card.max_health

        if deals_damage:
            opponent_card.health -= dmg['DMG']

        battle_log_message = (
            f"({battle_config.turn_total}) {dmg['MESSAGE']}\n"
            if deals_damage else
            f"({battle_config.turn_total})"
        )
        battle_log_message += f"[{self.name} ☠️ reaped {death_buff_value} health [+🗡️{death_buff_value:,}]"
        battle_config.add_to_battle_log(battle_log_message)

        if opponent_card.health <= (opponent_card.max_base_health * 0.10):
            opponent_card.health = 0
            opponent_card.max_health = 0
            battle_config.add_to_battle_log(
                f"({battle_config.turn_total}) ☠️ [{opponent_card.name} was executed by {self.name}]"
            )


    def life_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "LIFE":
            return
        
        deals_damage = not opponent_card.parry_active
        if self.title_blitz or self.title_strategist:
            deals_damage = True
        if deals_damage:
            opponent_card.health = round(opponent_card.health - dmg['DMG'])

        opponent_card.max_health = opponent_card.max_health - round(dmg['DMG'] * self.life_buff_value)
        self.max_health = self.max_health + round(dmg['DMG'] * self.life_buff_value)
        self.health = self.health + round((dmg['DMG'] * self.life_buff_value + (self.max_health * 0.05)))

        battle_log_message = (
            f"({battle_config.turn_total}) {dmg['MESSAGE']}\n"
            if deals_damage else
            f"({battle_config.turn_total})"
        )
        battle_log_message += f"[{self.name} ❤️‍🔥 stole {round(dmg['DMG'] * self.life_buff_value + (self.max_health * 0.05))} health]"
        battle_config.add_to_battle_log(battle_log_message)


    def nature_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "NATURE":
            return

        deals_damage = not opponent_card.parry_active
        if self.title_blitz or self.title_strategist:
            deals_damage = True
        if deals_damage:
            opponent_card.health = round(opponent_card.health - dmg['DMG'])
            

        opponent_card.attack = opponent_card.attack - (dmg['DMG'] * self.nature_debuff_value)
        opponent_card.defense = opponent_card.defense - (dmg['DMG'] * self.nature_debuff_value)
        opponent_card.health = opponent_card.health - dmg['DMG']
        nature_amount = round(dmg['DMG'] * self.nature_buff_value)
        self.attack = self.attack + (dmg['DMG'] * self.nature_buff_value)
        self.defense = self.defense + (dmg['DMG'] * self.nature_buff_value)
        self.health = self.health + (dmg['DMG'] * self.nature_buff_value)
        self.max_health = self.max_health + (dmg['DMG'] * self.nature_buff_value)
        self.max_base_health = self.max_base_health + (dmg['DMG'] * self.nature_buff_value)
        battle_log_message = (
            f"({battle_config.turn_total}) {dmg['MESSAGE']} "
            if deals_damage else
            f"({battle_config.turn_total})"
        )
        battle_log_message += f"\n[{self.name} sapped {nature_amount} attack & defense [+❤️{nature_amount:,} | 🗡️{nature_amount:,} | 🛡️{nature_amount:,}]"
        if opponent_card.defense <= 30:
            opponent_card.defense = 30
        if opponent_card.attack <= 30:
            opponent_card.attack = 30
        battle_config.add_to_battle_log(battle_log_message)


    def electric_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "ELECTRIC":
            return

        deals_damage = not opponent_card.parry_active
        if self.title_blitz or self.title_strategist:
            deals_damage = True
        if deals_damage:
            opponent_card.health = round(opponent_card.health - dmg['DMG'])

        self.shock_buff = self.shock_buff +  (dmg['DMG'] * self.electric_buff_value)
        opponent_card.health = opponent_card.health - dmg['DMG']

        battle_log_message = (
            f"({battle_config.turn_total}) {dmg['MESSAGE']}\n"
            if deals_damage else
            f"({battle_config.turn_total})"
        )
        battle_log_message += f"[{self.name} gained {round(dmg['DMG'] * self.electric_buff_value)} shock ap]"
        battle_config.add_to_battle_log(battle_log_message)


    def ice_effect_handler(self, battle_config, dmg, opponent_card):
        if dmg['ELEMENT'] != "ICE":
            return
        
        deals_damage = not opponent_card.parry_active
        if self.title_blitz or self.title_strategist:
            deals_damage = True
        if self.freeze_enh:
            deals_damage = True

        if deals_damage:
            opponent_card.health = round(opponent_card.health - dmg['DMG'])

        message = ""
        if self.ice_duration == 0:
            self.ice_counter += 1
            hits_remaining = 3 - self.ice_counter
            if hits_remaining > 0:
                message = f"[{hits_remaining} more {'hit' if hits_remaining == 1 else 'hits'} until {opponent_card.name} freezes]"
            else:
                message = f"[{opponent_card.name} is frozen {opponent_card.name} lost {round(dmg['DMG'] * .50):,} attack and defense]"
                self.freeze_enh = True
                self.ice_duration = self.ice_buff_value
                self.ice_counter = 0
                opponent_card.attack = opponent_card.attack - (dmg['DMG'] * .50)
                opponent_card.defense = opponent_card.defense - (dmg['DMG'] * .50)
                # write to battle log that the opponent lost attack and defense
                if opponent_card.defense <= 30:
                    opponent_card.defense = 30
                if opponent_card.attack <= 30:
                    opponent_card.attack = 30
                

        battle_log_message = (
            f"({battle_config.turn_total}) {dmg['MESSAGE']}\n"
            if deals_damage else
            f"({battle_config.turn_total})"
        )
        battle_log_message += f"\n{message}"
        battle_config.add_to_battle_log(battle_log_message)
        battle_config.add_to_battle_log()

    def gun_effect_handler(self, battle_config, dmg, opponent_card):
        opponent_card.health = opponent_card.health - dmg['DMG']
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}")
        # create a condition where there's a 20% chance to hit again, then send message to battle log that the attack hit again
        if random.randint(1, 100) <= 40:
            opponent_card.defense = opponent_card.defense - (opponent_card.defense * .35)
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} shot again for {dmg['DMG']} damage")
        
    def time_effect_handler(self, battle_config, dmg, opponent_card):
        if self.stamina <= 50:
            self.stamina = 0
            self.card_lvl_ap_buff = self.card_lvl_ap_buff + (round(dmg['DMG'] * ((battle_config.turn_total + 1) / 100)))
        self.used_block = True
        self.defense = round(self.defense * self.time_buff_by_value)
        battle_config.turn_total = battle_config.turn_total + 3
        opponent_card.health = opponent_card.health - dmg['DMG']
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']} [+3 turns]")

    def physical_effect_handler(self, battle_config, dmg, opponent_card):
        self.physical_meter = self.physical_meter + 1
        if self.physical_meter == 2:
            self.parry_active = True
            self._parry_value = self._parry_value + self.physical_parry_value
            add_solo_leveling_temp_values(self, 'PARRY', opponent_card)
            self.physical_meter = 0
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}\n[{self.name} gained {self.physical_parry_value} parry 🔄]")
        else:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}")
        opponent_card.health = opponent_card.health - dmg['DMG']

    def ranged_effect_handler(self, battle_config, dmg, opponent_card):
        self.ranged_meter = self.ranged_meter + 1
        if self.ranged_meter == 2:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}\n[{self.name} aims]")
        elif self.ranged_meter == 3:
            self.ranged_meter = 0
            self.ranged_hit_bonus = self.ranged_hit_bonus + self.ranged_buff_value
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}\n[{self.name} increased {self.ranged_hit_bonus * 5}% accuracy]")
        else:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}")
        opponent_card.health = opponent_card.health - dmg['DMG']

    def reckless_effect_handler(self, battle_config, dmg, opponent_card):
        self.health = self.health - (dmg['DMG'] * self.reckless_buff_value)
        if self.used_resolve:
            self.reckless_buff_value = .30
        if self.health <= 0:
            self.health = 1
        if self.reckless_duration <= 0 and not dmg['SUMMON_USED']:
            if not self.used_resolve:
                self.reckless_duration = 1
                self.reckless_rest = True
            else:
                self.reckless_duration = 0
                self.reckless_rest = True
        opponent_card.health = opponent_card.health - dmg['DMG']
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}\n[{self.name} was dealt {str(round(dmg['DMG'] * self.reckless_buff_value))} reckless damage]")

    def psychic_effect_handler(self, battle_config, dmg, opponent_card):
        self.barrier_meter = self.barrier_meter + 1
        debuff_value = round(dmg['DMG'] * self.psychic_debuff_value)
        if self.barrier_meter == 3:
            self.barrier_active = True
            self._barrier_value = self._barrier_value + self.psychic_barrier_buff_value
            add_solo_leveling_temp_values(self, 'BARRIER', opponent_card)
            self.barrier_meter = 0
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}\n[{self.name} gained {self.psychic_barrier_buff_value} 💠 barrier [{opponent_card.name} lost {debuff_value} attack and defense]")
        else:    
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}\n[{opponent_card.name} lost {debuff_value} attack and defense]")

        opponent_card.defense = opponent_card.defense - debuff_value
        opponent_card.attack = opponent_card.attack - debuff_value
        opponent_card.health = opponent_card.health - dmg['DMG']
        if opponent_card.defense <= 30:
            opponent_card.defense = 30
        if opponent_card.attack <= 30:
            opponent_card.attack = 30


    def sleep_effect_handler(self, battle_config, dmg, opponent_card):
        sleep_stacks_added = 0
        if not self.sleep_exhaustion_bool:
            self.sleep_counter = self.sleep_counter + 1
            if self.sleep_counter == 2:
                self.sleep_counter = 0
                sleep_stacks_added = random.choice([1, 2, 3])
                self.sleep_rest_skips = self.sleep_rest_skips + sleep_stacks_added
                sleep_message = f"({battle_config.turn_total}) {self.name} added 💤 {sleep_stacks_added} sleep stacks [{self.sleep_rest_skips} total sleep stacks]"
            else:
                sleep_message = f"({battle_config.turn_total}) {self.name} is prepping to add 💤 sleep stacks on next hit"
            battle_config.add_to_battle_log(sleep_message)

        if self.sleep_exhaustion_bool or opponent_card.reckless_rest:
            opponent_card.health = opponent_card.health - dmg['DMG']
            sleep_message = f"({battle_config.turn_total}) 💤 {dmg['MESSAGE']}"
            battle_config.add_to_battle_log(sleep_message)

    def poison_effect_handler(self, battle_config, dmg, opponent_card):
        poison_capacity = self.max_health * .30
        if self.poison_dmg <= poison_capacity:
            poison_damage_from_ability = round(self.poison_dmg + (dmg['DMG'] * self.poison_damage_value))
            self.poison_dmg = self.poison_dmg + poison_damage_from_ability
        if self.poison_dmg > poison_capacity:
            self.poison_dmg = poison_capacity
        
        poison_capacity_message = f"({battle_config.turn_total}) 🧪 {self.name} injects poison! {opponent_card.name} will now take {round(self.poison_dmg):,} damage when attacking."
        if self.poison_dmg == poison_capacity:
            poison_capacity_message = f"({battle_config.turn_total}) 🧪 {self.name}'s injected maximum poison! {opponent_card.name} will now take {round(self.poison_dmg):,} damage when attacking."
        battle_config.add_to_battle_log(poison_capacity_message)

    def rot_effect_handler(self, battle_config, dmg, opponent_card):
        rot_capacity = self.max_health * .20
        if self.rot_dmg <= rot_capacity:
            rot_damage_from_ability = round(self.rot_dmg + (dmg['DMG'] * self.rot_damage_value))
            self.rot_dmg = self.rot_dmg + rot_damage_from_ability
        if self.rot_dmg > rot_capacity:
            self.rot_dmg = rot_capacity
        
        rot_capacity_message = f"({battle_config.turn_total}) 🩻 {self.name} inflits rot! {opponent_card.name} will now take {round(self.rot_dmg):,} damage to max health when attacking."
        if self.rot_dmg == rot_capacity:
            rot_capacity_message = f"({battle_config.turn_total}) 🩻 {self.name}'s inflicted maximum rot! {opponent_card.name} will now take {round(self.rot_dmg):,} damage to max health when attacking."
        battle_config.add_to_battle_log(rot_capacity_message)

    def bleed_effect_handler(self, battle_config, dmg, opponent_card):
        self.bleed_damage_counter = self.bleed_damage_counter + 1
        if self.bleed_damage_counter == 2:
            self.bleed_hit = True
            self.bleed_damage_counter = 0
        opponent_card.health = opponent_card.health - dmg['DMG']
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}")

    def gravity_effect_handler(self, battle_config, dmg, opponent_card):
        battle_config.turn_total = battle_config.turn_total - 3
        if (battle_config.turn_total - 3) < 0:
            battle_config.turn_total = 0
        self.gravity_hit = True
        opponent_card.health = opponent_card.health - dmg['DMG']
        opponent_card.defense = opponent_card.defense - (dmg['DMG'] * self.gravity_debuff_value)
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']} [-3 turns]")

    def active_shield_handler(self, battle_config, dmg, opponent_card, player_title, opponent_title):
        if opponent_card.shield_active:
            attacker = self.name
            if dmg['SUMMON_USED']:
                attacker = f"{self.summon_name}"

            if self._assassin_active:
                return False

            
            if not opponent_title.impenetrable_shield_effect:
                if dmg['ELEMENT'] in ["DARK", "POISON", "ROT", "SLEEP", "DRACONIC"]:
                    return False
                if player_title.obliterate_effect:
                    self.title_obliterate = True
                    return False
                
                if player_title.strategist_effect:
                    self.title_strategist = True
                    return False
    
                self.water_effect_handler(battle_config, dmg, opponent_card)

                
                if self.energy_crit_bool:
                    self.energy_crit_bool = False
                    
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} 🧿 critically struck through {opponent_card.name} shield")
                    return False
                
                
            if self.barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                if not dmg['SUMMON_USED'] and not self.is_ranger:
                    self.barrier_active = False
                    self._barrier_value = 0
                    self._arm_message = ""
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} disengaged their barrier to engage with an attack")
                    decrease_solo_leveling_temp_values(self, 'BARRIER', opponent_card, battle_config)

            if dmg['ELEMENT'] == "FIRE":
                self.burn_dmg = self.burn_dmg + round(dmg['DMG'] * .50)
            if opponent_card._shield_value > 0:
                damage_absorbed_message = opponent_title.spell_shield_handler(self, dmg, battle_config)
                if damage_absorbed_message:
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {damage_absorbed_message}")
                    return
                opponent_card._shield_value = opponent_card._shield_value - dmg['DMG']
                # opponent_card.health = opponent_card.health 
                if opponent_card._shield_value <= 0:
                    opponent_card.shield_active = False
                    opponent_card._arm_message = ""
                    residue_damage = abs(opponent_card._shield_value)
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🌐 {opponent_card.name}'s shield was shattered, taking {round(residue_damage):,} damage")
                    self.stats_incrimintation(dmg, residue_damage)
                    decrease_solo_leveling_temp_values_self(self, 'SHIELD', battle_config)
                    opponent_card.health = opponent_card.health - residue_damage
                    self.damage_dealt = self.damage_dealt +  residue_damage
                    if opponent_card.barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                        opponent_card.barrier_active = False
                        opponent_card._barrier_value = 0
                        opponent_card._arm_message = ""
                        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} destroys {opponent_card.name} 💠 barrier")
                        decrease_solo_leveling_temp_values_self(self, 'BARRIER', battle_config)
                else:
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} strikes {opponent_card.name}'s shield 🌐 [{round(opponent_card._shield_value):,} shield left]")
                    if opponent_card.barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                        opponent_card.barrier_active = False
                        opponent_card._barrier_value = 0
                        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} destroyed {opponent_card.name}'s 💠 barrier [0 barriers left]")
                        decrease_solo_leveling_temp_values_self(self, 'BARRIER', battle_config)
            
            return True
        else:
            return False


    def active_barrier_handler(self, battle_config, dmg, opponent_card, player_title, opponent_title):
        if opponent_card.barrier_active:
            attacker = self.name
            if dmg['SUMMON_USED']:
                attacker = f"{self.summon_name}"
                
            if self._assassin_active:
                return False
            
            if dmg['ELEMENT'] in ["PSYCHIC", "DARK", "TIME", "GRAVITY", "DRACONIC"]:
                if dmg['ELEMENT'] == "TIME" and opponent_card._barrier_value > 1:
                    opponent_card._barrier_value = opponent_card._barrier_value - 1
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} reduces {opponent_card.name} barrier 💠 [{opponent_card._barrier_value} barriers left]")
                if dmg['ELEMENT'] == "TIME" and opponent_card._barrier_value == 1:
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} destroys {opponent_card.name} 💠 barrier")
                    opponent_card._barrier_value = opponent_card._barrier_value - 1
                    opponent_card.barrier_active = False
                    opponent_card._barrier_value = 0
                    opponent_card._arm_message = ""
                    decrease_solo_leveling_temp_values_self(self, 'BARRIER', battle_config)
                
                return False

            if dmg['ELEMENT'] == "SLEEP":
                return False

            if player_title.pierce_effect:
                self.title_pierce = True
                return False
            
            if player_title.strategist_effect:
                self.title_strategist = True
                return False
            
            

            if self.energy_crit_bool:
                self.energy_crit_bool = False
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} 🧿 critically struck through {opponent_card.name} barriers")
                return False

            if self.barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                if not dmg['SUMMON_USED'] and not self.is_ranger:
                    self.barrier_active = False
                    self._barrier_value = 0
                    self._arm_message = ""
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} disengaged their barrier to engage with an attack")
                    self.decrease_solo_leveling_temp_values('BARRIER', opponent_card, battle_config)
            if opponent_card._barrier_value > 1:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} hits {opponent_card.name} barrier 💠 [{opponent_card._barrier_value - 1} barriers left]")
                if opponent_card.barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                    opponent_card.barrier_active = False
                    opponent_card._barrier_value = 0
                    opponent_card._arm_message = ""
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} destroys {opponent_card.name} 💠 barrier")
                    decrease_solo_leveling_temp_values_self(self, 'BARRIER', battle_config)
                opponent_card._barrier_value = opponent_card._barrier_value - 1
            elif opponent_card._barrier_value == 1:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} destroys {opponent_card.name} 💠 barrier")
                opponent_card._barrier_value = opponent_card._barrier_value - 1
                opponent_card.barrier_active = False
                opponent_card._barrier_value = 0
                opponent_card._arm_message = ""
                decrease_solo_leveling_temp_values_self(self, 'BARRIER', battle_config)            
            return True
        else:
            return False
    

    def active_parry_handler(self, battle_config, dmg, opponent_card, player_title, opponent_title):
        if opponent_card.parry_active:
            attacker = self.name
            if dmg['SUMMON_USED']:
                attacker = f"{self.summon_name}"

            if self._assassin_active:
                return False
            
            if dmg['ELEMENT'] in ["POISON", "ROT", "SLEEP", "BLEED", "DRACONIC"]:
                return False
            
            if dmg['ELEMENT'] in ["EARTH", "DARK", "PSYCHIC", "TIME", "GRAVITY"]:
                if dmg['ELEMENT'] == "TIME" and opponent_card._parry_value > 1:
                    opponent_card._parry_value = opponent_card._parry_value - 1
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} hits {opponent_card.name} parry 🔄 [{opponent_card._parry_value} parries left]")
                if dmg['ELEMENT'] == "TIME" and opponent_card._parry_value == 1:
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} penetrates {opponent_card.name}'s parry 🔄")
                    opponent_card._parry_value = opponent_card._parry_value - 1
                    opponent_card.parry_active = False
                    opponent_card._parry_value = 0
                    opponent_card._arm_message = ""
                    decrease_solo_leveling_temp_values_self(self, 'PARRY', battle_config)

                return False
            
            if player_title.blitz_effect:
                self.title_blitz = True
                return False

            if player_title.strategist_effect:
                self.title_strategist = True
                return False
            

            if dmg['ELEMENT'] in ["LIGHT", "FIRE", "WATER", "EARTH", "DEATH", "LIFE", "NATURE", "ELECTRIC", "ICE"]:
                self.light_effect_handler(battle_config, dmg, opponent_card)
                self.fire_effect_handler(battle_config, dmg, opponent_card)
                self.water_effect_handler(battle_config, dmg, opponent_card)
                self.earth_effect_handler(battle_config, dmg, opponent_card)
                self.death_effect_handler(battle_config, dmg, opponent_card)
                self.life_effect_handler(battle_config, dmg, opponent_card)
                self.nature_effect_handler(battle_config, dmg, opponent_card)
                self.electric_effect_handler(battle_config, dmg, opponent_card)
                self.ice_effect_handler(battle_config, dmg, opponent_card)


            if self.energy_crit_bool:
                self.energy_crit_bool = False
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} 🧿 critically struck through {opponent_card.name} parry")
                return False

            parry_damage_percentage = .50
            if player_title.foresight_effect:
                parry_damage_percentage = .05
            if self.barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                if not dmg['SUMMON_USED'] and not self.is_ranger:
                    self.barrier_active = False
                    self._barrier_value = 0
                    self._arm_message = ""
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} disengaged their barrier to engage with an attack")
                    decrease_solo_leveling_temp_values(self, 'BARRIER', opponent_card, battle_config)
            if opponent_card._parry_value > 1:
                parry_damage = round(dmg['DMG'])
                opponent_card.health = round(opponent_card.health - (parry_damage * .75))
                self.health = round(self.health - (parry_damage * parry_damage_percentage))
                self.damage_dealt = self.damage_dealt +  (parry_damage * .75)
                opponent_card._parry_value = opponent_card._parry_value - 1
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {opponent_card.name} parried 🔄 {attacker}'s attack dealing {round(parry_damage * .50):,} damage, and taking {round(parry_damage * .75):,} damage [{opponent_card._parry_value} parries left]")
                dmg['DMG'] = parry_damage * .75
                self.stats_incrimintation(dmg)
                if opponent_card.health <= 0 and self.health <= 0:
                    opponent_card.health = 1
                if opponent_card.barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                    opponent_card.barrier_active = False
                    opponent_card._barrier_value = 0
                    opponent_card._arm_message = ""
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} destroys {opponent_card.name} 💠 barrier")
                    decrease_solo_leveling_temp_values_self(self, 'PARRY', battle_config)
            elif opponent_card._parry_value == 1:
                parry_damage = round(dmg['DMG'])
                opponent_card.health = round(opponent_card.health - (parry_damage * .75))
                self.health = round(self.health - (parry_damage * parry_damage_percentage))
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} broke {opponent_card.name}'s parry 🔄 dealing {round(parry_damage * .75):,} damage, taking {round(parry_damage * .50):,} damage [0 parries left]")
                dmg['DMG'] = parry_damage * .75
                self.stats_incrimintation(dmg)
                if opponent_card.health <= 0 and self.health <= 0:
                    opponent_card.health = 1
                opponent_card._parry_value = opponent_card._parry_value - 1
                if opponent_card.barrier_active and dmg['ELEMENT'] == "PSYCHIC":
                    opponent_card.barrier_active = False
                    opponent_card._barrier_value = 0
                    opponent_card._arm_message = ""
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {attacker} destroys {opponent_card.name} 💠 barrier")
                    decrease_solo_leveling_temp_values_self(self, 'BARRIER', battle_config)
                opponent_card.parry_active = False
                opponent_card._parry_value = 0
                opponent_card._arm_message = ""
                decrease_solo_leveling_temp_values_self(self, 'PARRY', battle_config)

            return True
        else:
            return False


    def direct_hit_handler(self, battle_config, dmg, opponent_card, naruto_trait_active, protection_enabled):
        if not protection_enabled:
            # If assassin_strike is greater than 0, reduce asssassin strike by 1
            if self.universe == "One Piece" and (self.tier in crown_utilities.LOW_TIER_CARDS or self.tier in crown_utilities.MID_TIER_CARDS or self.tier in crown_utilities.HIGH_TIER_CARDS):
                if self.focus_count == 0:
                    dmg['DMG'] = dmg['DMG'] * .6
            if self.universe == "Chainsawman":
                contracts(self, dmg, battle_config)
            if self.siphon_active:
                siphon_damage = (dmg['DMG'] * .15) + self._siphon_value
                self.damage_healed = self.damage_healed + (dmg['DMG'] * .15) + self._siphon_value
                self.health = round(self.health + siphon_damage)
                if self.health >= self.max_health:
                    self.health = self.max_health
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} 💉 siphoned and now has full health")
                else:
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} 💉 siphoned {round(siphon_damage):,} health")
            
            if self.barrier_active and dmg['ELEMENT'] != "PSYCHIC":
                if not dmg['SUMMON_USED'] and not self.is_ranger:
                    self.barrier_active = False
                    self._barrier_value = 0
                    self._arm_message = ""
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} disengaged their barrier to engage with an attack")

            self.stats_incrimintation(dmg)
            self.activate_element_check(battle_config, dmg, opponent_card)
        else:
            self.set_poison_hit(battle_config, opponent_card)
            self.set_rot_hit(battle_config, opponent_card)
            pass


    def regeneration_handler(self, battle_config, dmg, opponent_card):
        if opponent_card.health <= 0:
            if opponent_card.regeneration:
                #print("Regeneration activated")
                if not opponent_card.regeneration_activated:
                    if battle_config.turn_total >= 80:
                        opponent_card.regeneration_activated = True
                        opponent_card.health = opponent_card.max_base_health
                        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {opponent_card.name} took a fatal blow but... [Regeneration Activated]!")
                        battle_config.next_turn()
                        return
            else:
                opponent_card.health = 0

    
    def stats_incrimintation(self, dmg, residue_damage=0):
        if dmg['STAMINA_USED'] == 10:
            self.move1_damage_dealt = self.move1_damage_dealt + dmg['DMG'] + residue_damage
        if dmg['STAMINA_USED'] == 30:
            self.move2_damage_dealt = self.move2_damage_dealt + dmg['DMG'] + residue_damage
        if dmg['STAMINA_USED'] == 80:
            self.move3_damage_dealt = self.move3_damage_dealt + dmg['DMG'] + residue_damage
                

    def attack_handler(self, battle_config, dmg, opponent_card):
        turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

        if not dmg['REPEL'] and not dmg['ABSORB']:
            if opponent_card.jujutsu_kaisen_domain_expansion_active:
                domain_expansion_check(self, opponent_card, battle_config, dmg['DMG'])
                return

            if dmg['SUMMON_USED']:
                name = f"🧬 {self.name} summoned **{self.summon_name}**\n"
            else:
                name = f" **{self.name}:**"
            
            naruto_trait_active = substitution_jutsu(self, opponent_card, dmg, battle_config)
            if naruto_trait_active:
                return

            protection_handlers = [
                self.active_barrier_handler,
                self.active_shield_handler,
                self.active_parry_handler,
            ]

            protection_enabled = False

            for handler in protection_handlers:
                active = handler(battle_config, dmg, opponent_card, turn_title, opponent_title)
                if active:
                    protection_enabled = True
                    break
            
            self.direct_hit_handler(battle_config, dmg, opponent_card, naruto_trait_active, protection_enabled)
            
            self.regeneration_handler(battle_config, dmg, opponent_card)

            final_stand(self, battle_config, dmg, opponent_card)
            devils_endurance(opponent_card, battle_config)
            #Check for Fire Poison Etc Here
            # battle_config.turn_total = battle_config.turn_total + 1
        else:
            return


    def damage_done(self, battle_config, dmg, opponent_card):
        try:
            if dmg['CAN_USE_MOVE'] and dmg['CAN_USE_MOVE'] is not None:
                print(dmg)
                enhancer_used = self.enhancer_handler(battle_config, dmg, opponent_card)
                attack_missed = False
                if not enhancer_used:
                    attack_missed = self.missed_attack_handler(battle_config, dmg, opponent_card)          
                
                if not any([enhancer_used, attack_missed]):
                    self.attack_handler(battle_config, dmg, opponent_card)
                battle_config.turn_total = battle_config.turn_total + 1
            else:
                print("Something broke in the above code")
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} not enough stamina to use this move")
                battle_config.repeat_turn()
        except Exception as e:
            print(e)
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {self.name} not enough stamina to use this move")
            battle_config.next_turn()

    
    # If protections isn't hit ALL damage done to opponent health is tracked here
    def activate_element_check(self, battle_config, dmg, opponent_card):
        if dmg['REPEL']:
            self.health = self.health - dmg['DMG']
        
        if dmg['ABSORB']:
            opponent_card.health = opponent_card.health + dmg['DMG']

        if dmg['SUMMON_USED']:
            name = f"({battle_config.turn_total}) 🧬 {self.name} summoned {self.summon_name}"
        else:
            name = f"({battle_config.turn_total}) {self.name}"

        if dmg['ELEMENT'] == "WATER":
            self.water_effect_handler(battle_config, dmg, opponent_card)
        
        elif dmg['ELEMENT'] == "GUN":
            self.gun_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "TIME":
            self.time_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "EARTH":
            self.earth_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "DEATH":
            self.death_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "LIGHT":
            self.light_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "DARK":
            self.dark_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "DRACONIC":
            self.draconic_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "PHYSICAL":
            self.physical_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "RANGED":
            self.ranged_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "LIFE":
            self.life_effect_handler(battle_config, dmg, opponent_card)
        
        elif dmg['ELEMENT'] in ["RECKLESS", "RECOIL"]:
            self.reckless_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "PSYCHIC":
            self.psychic_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "NATURE":
            self.nature_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "FIRE":
            self.fire_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "ELECTRIC":
            self.electric_effect_handler(battle_config, dmg, opponent_card)
 
        elif dmg['ELEMENT'] == "SLEEP":
            self.sleep_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "POISON":
            self.poison_effect_handler(battle_config, dmg, opponent_card)

        elif dmg['ELEMENT'] == "ROT":
            self.rot_effect_handler(battle_config, dmg, opponent_card)


        elif dmg['ELEMENT'] == "ICE":
            self.ice_effect_handler(battle_config, dmg, opponent_card)


        elif dmg['ELEMENT'] == "BLEED":
            self.bleed_effect_handler(battle_config, dmg, opponent_card)

        
        elif dmg['ELEMENT'] == "GRAVITY":
            self.gravity_effect_handler(battle_config, dmg, opponent_card)
        
        else:
            opponent_card.health = opponent_card.health - dmg['DMG']
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {dmg['MESSAGE']}")
        
        self.set_poison_hit(battle_config, opponent_card)
        self.set_rot_hit(battle_config, opponent_card)
        self.element_selection.append(dmg['ELEMENT'])
        self.damage_dealt = self.damage_dealt + dmg['DMG']
        opponent_card.damage_received = opponent_card.damage_received + dmg['DMG']


    def reset_stats_to_limiter(self, _opponent_card):
        try:
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
            
            if self.attack > 20000:
                self.attack = 20000
            
            if self.defense > 20000:
                self.defense = 20000
            
            if _opponent_card.attack > 20000:
                _opponent_card.attack = 20000
            
            if _opponent_card.defense > 20000:
                _opponent_card.defense = 20000
        
            if self.health >= self.max_health:
                self.health = self.max_health
                
            if _opponent_card.health >= _opponent_card.max_health:
                _opponent_card.health = _opponent_card.max_health
            
            if self.used_resolve and self.universe == "Souls":
                self.move1ap = self.move2base + round(self.card_lvl_ap_buff + self.shock_buff + self.special_water_buff + self.arbitrary_ap_buff)
                self.move2ap = self.move3base + round(self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff)
                self.move3ap = self.move3base + round(self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff)
            elif self.used_resolve and self.universe == "That Time I Got Reincarnated as a Slime":
                self.move1ap = 25
                self.move2ap = 25
                self.move3ap = self.move3base + round(self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff + self.slime_buff)
            else:
                self.move1ap = self.move1base + round(self.card_lvl_ap_buff + self.shock_buff + self.basic_water_buff + self.arbitrary_ap_buff + self.yuyu_1ap_buff + self.my_hero_academia_buff + self.bleach_fullbring_ap_buff + self.bleach_hollow_ap_buff)
                self.move2ap = self.move2base + round(self.card_lvl_ap_buff + self.shock_buff + self.special_water_buff + self.arbitrary_ap_buff + self.yuyu_2ap_buff + self.my_hero_academia_buff + self.bleach_fullbring_ap_buff + self.bleach_hollow_ap_buff)
                self.move3ap = self.move3base + round(self.card_lvl_ap_buff + self.shock_buff + self.ultimate_water_buff + self.arbitrary_ap_buff + self.yuyu_3ap_buff + self.my_hero_academia_buff + self.slime_buff + self.bleach_fullbring_ap_buff + self.bleach_hollow_ap_buff + self.bleach_quincy_ap_buff)
            
            # _opponent_card.move1ap = _opponent_card.list(self.m1.values())[0] + _opponent_card.card_lvl_ap_buff + _opponent_card.shock_buff + _opponent_card.basic_water_buff + _opponent_card.arbitrary_ap_buff
            # _opponent_card.move2ap = _opponent_card.list(self.m2.values())[0] + _opponent_card.card_lvl_ap_buff + _opponent_card.shock_buff + _opponent_card.basic_water_buff + _opponent_card.arbitrary_ap_buff
            # _opponent_card.move3ap = _opponent_card.list(self.m3.values())[0] + _opponent_card.card_lvl_ap_buff + _opponent_card.shock_buff + _opponent_card.basic_water_buff + _opponent_card.arbitrary_ap_buff
        except Exception as ex:
            custom_logging.debug(ex)


    def get_tactics(self, battle_config):
        if self._is_boss or battle_config.is_raid_scenario:
            self.tactics = battle_config._tactics
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
                    self.damage_check_limit = round(random.randint(1000, 3500))


    def stats_handler(self, battle_config, player, total_complete):
        moves = [
            {"element": self.move1_element, "damage_dealt": self.move1_damage_dealt},
            {"element": self.move2_element, "damage_dealt": self.move2_damage_dealt},
            {"element": self.move3_element, "damage_dealt": self.move3_damage_dealt}
        ]
        stats.update_stats(player, battle_config, self.damage_dealt, self.damage_received, self.damage_healed, moves, total_complete)

                        
    def set_stat_icons(self):
        if self.used_focus:
            self.focus_icon = '💖'
        if self.used_resolve:
            self.resolve_icon = '⚡'

    def set_health_color(self):
        self.health_color = crown_utilities.health_color(self.health, self.max_health)
        return self.health_color

    def get_performance_stats(self):
        if round(self.health) == round(self.max_health):
            return f"**Current Stats**\n{self.focus_icon} | **{round(self.health)}** *Health*\n{self.resolve_icon} | **{self.stamina}** *Stamina*"
        return f"**Current Stats**\n{self.focus_icon} | **{round(self.health)}** / *{round(self.max_health)} Health*\n{self.resolve_icon} | **{self.stamina}** *Stamina*"
    

    def get_perfomance_header(self, player_title):
        if len(player_title.name) > 20:
            player_title.name = player_title.name[:17] + "..."
        if self._arm_message != "":
            return f"{self.get_performance_stats()}\n{player_title.get_title_icon(self.universe)} | *{player_title.name}* **{player_title.passive_type.title()} {player_title.passive_value}{crown_utilities.title_enhancer_suffix_mapping[player_title.passive_type]}**\n**{self._arm_message}**"
        else:
            return f"{self.get_performance_stats()}\n{player_title.get_title_icon(self.universe)} | *{player_title.name}* **{player_title.passive_type.title()} {player_title.passive_value}{crown_utilities.title_enhancer_suffix_mapping[player_title.passive_type]}**"
    

    def get_performance_moveset(self):
        if len(self.move1) > 20:
            self.move1 = self.move1[:17] + "..."
        if len(self.move2) > 20:
            self.move2 = self.move2[:17] + "..."
        if len(self.move3) > 20:
            self.move3 = self.move3[:17] + "..."
        if len(self.move4) > 20:
            self.move4 = self.move4[:17] + "..."
        if self.used_resolve:
            return f"{self.move1_emoji} 10 | *{self.move1}* **{self.move1ap}**\n{self.move2_emoji} 30 | *{self.move2}* **{self.move2ap}**\n{self.move3_emoji} 80 | *{self.move3}* **{self.move3ap}**\n:microbe: 20 | *{self.move4}* **{self.move4enh.title()} {self.move4ap}**\n*{self.summon_resolve_message}*"
        else:
            return f"{self.move1_emoji} 10 | *{self.move1}* **{self.move1ap}**\n{self.move2_emoji} 30 | *{self.move2}* **{self.move2ap}**\n{self.move3_emoji} 80 | *{self.move3}* **{self.move3ap}**\n:microbe: 20 | *{self.move4}* **{self.move4enh.title()} {self.move4ap}**"
        
    def get_card_dict(self):
        '''
        Returns the card class as a dictionary
        Capitalize all keys
        '''
        card_dict = {}
        for key, value in self.__dict__.items():
            card_dict[key.upper()] = value
        return card_dict

def get_card(url, cardname, cardtype):
        try:
            im = Image.open(requests.get(url, stream=True).raw)
            return im   
        except Exception as ex:
            custom_logging.debug(ex)


def calculate_font_sizes(name, rname, used_resolve):
    name_font_size = 60
    title_font_size = 35
    basic_font_size = 30
    super_font_size = 30
    ultimate_font_size = 30
    enhancer_font_size = 30
    title_size = (600, 65)


    name_length = max(len(name), len(rname))

    if name_length >= 28:
        name_font_size = 30
        title_size = (600, 80)
    elif name_length >= 25:
        name_font_size = 34
        title_size = (600, 80)
    elif name_length >= 18:
        name_font_size = 40
        title_size = (600, 80)
    elif name_length >= 15:
        name_font_size = 45

    return name_font_size, title_font_size, basic_font_size, super_font_size, ultimate_font_size, enhancer_font_size, title_size


def calculate_engagement_levels(opponent_card_defense, mode, player):
    if mode == "non-battle" or opponent_card_defense is None:
        return "", "", "", 0, 0, 0
    
    def calculate_engagement(attack_power, move_ap):
        defense_power = max(opponent_card_defense - attack_power, 1)
        ability_power = max(attack_power - opponent_card_defense + move_ap, move_ap)
        ratio = round(ability_power / defense_power)
        
        if ratio > 2 * move_ap: return '❌x2', 5
        if ratio > 1.5 * move_ap: return '〽️x1.5', 4
        if ratio >= 1.1 * move_ap: return '‼️', 3
        if move_ap / 2 > ratio > move_ap / 3: return '❕', 2
        if ratio < move_ap / 3: return '💢', 1
        return '💢', 1  # Default case if none above match
    
    results = [calculate_engagement(player.attack, getattr(player, f"move{idx}ap")) for idx in range(1, 4)]
    return (*[res[0] for res in results], *[res[1] for res in results])


def calculate_move_text_and_font_sizes(self, turn_total, ebasic, especial, eultimate):
    if len(self.move1) > 25:
        self.move1 = self.move1[:25] + "..."
    if len(self.move2) > 25:
        self.move2 = self.move2[:25] + "..."
    if len(self.move3) > 25:
        self.move3 = self.move3[:25] + "..."
    if len(self.move4) > 25:
        self.move4 = self.move4[:15] + "..."

    # Original with move engagement emojis
    # move1_text = f"{self.move1_emoji} {self.move1}: {self.move1ap} {ebasic}"
    # move2_text = f"{self.move2_emoji} {self.move2}: {self.move2ap} {especial}"
    # move3_text = f"{self.move3_emoji} {self.move3}: {self.move3ap} {eultimate}"
        
    move1_text = f"{self.move1_emoji} {self.move1}: {self.move1ap}"
    move2_text = f"{self.move2_emoji} {self.move2}: {self.move2ap}"
    #Added Draconic Check Here? 
    if self.move3_element == "DRACONIC":
        self.move3ap = round(self.move1ap + self.move2ap)
    move3_text = f"{self.move3_emoji} {self.move3}: {self.move3ap}"

    turn_crit = False
    if self.move4enh in crown_utilities.Turn_Enhancer_Check:
        if turn_total == 0:
            self.move4ap = round(self.move4base)
            turn_crit = True
        elif turn_total % 10 == 0:
            self.move4ap = round(self.move4base)
            turn_crit = True
        elif turn_total >= 1:
            self.move4ap = round(self.move4base / turn_total)
    
    if self.move4enh in crown_utilities.Damage_Enhancer_Check:
        if turn_total > 0:
            self.move4ap = round(self.move4base * turn_total)
            if self.move4ap >= (100 * self.tier):
                if self.move4enh == "BLAST":
                    self.move4ap = (100 * self.tier)
                else:
                    self.move4ap = (100 * self.tier)
                turn_crit = True

    if not turn_crit:
        move_enhanced_text = f"🦠 {self.move4}: {self.move4enh.title()} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"
    elif self.move4enh in crown_utilities.Damage_Enhancer_Check and self.move4ap == (100 * self.tier):
        move_enhanced_text = f"🎇 {self.move4}: {self.move4enh.title()} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"
    elif self.move4enh in crown_utilities.Turn_Enhancer_Check and (turn_total % 10 == 0 or turn_total == 0):
        move_enhanced_text = f"🎇 {self.move4}: {self.move4enh.title()} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"
    else:
        move_enhanced_text = f"🎇 {self.move4}: {self.move4enh.title()} {self.move4ap}{crown_utilities.enhancer_suffix_mapping[self.move4enh]}"
    
    basic_length = int(len(move1_text))
    super_length = int(len(move2_text))
    ultimate_length = int(len(move3_text))
    enhancer_length = int(len(move_enhanced_text))
        
    def calculate_font_size(length):
        if length >= 65:
            return 35
        elif length >= 60:
            return 37
        elif length >= 53:  # This implicitly covers the case where length <= 53 too
            return 39
        else:
            return 27  # Default font size if none of the above conditions are met

    basic_length = 54  # Example length
    super_length = 61  # Example length
    ultimate_length = 66  # Example length
    enhancer_length = 53  # Example length

    # Calculate font sizes using the function
    basic_font_size = calculate_font_size(basic_length)
    super_font_size = calculate_font_size(super_length)
    ultimate_font_size = calculate_font_size(ultimate_length)
    enhancer_font_size = calculate_font_size(enhancer_length)

    # Now, basic_font_size, super_font_size, ultimate_font_size, and enhancer_font_size 
    # will have values based on their respective lengths.

    return move1_text, move2_text, move3_text, move_enhanced_text, basic_font_size, super_font_size, ultimate_font_size, enhancer_font_size


def get_character_name_and_health_bar(self, draw, header, title_size):
    if self.health == self.max_health:
        health_bar = f"{format_number(round(self.max_health))}"
    else:
        health_bar = f"{format_number(round(self.health))}/{format_number(round(self.max_health))}"

    character_name = self.name.title()
    
    draw.text(title_size, character_name, (255, 255, 255), font=header, stroke_width=1, stroke_fill=(0, 0, 0),
              align="left")
    
    return health_bar, character_name


def get_lvl_sizing(self, draw, lvl_font):
    if int(self.card_lvl) <= 9:
        lvl_sizing = (90, 70)
    if int(self.card_lvl) > 9:
        lvl_sizing = (75, 70)
    if int(self.card_lvl) > 99:
        lvl_sizing = (55, 70)
    if int(self.card_lvl) > 999:
        lvl_sizing = (45, 70)
    # if card level is greater than 1000, we can default to a smaller font size


    def get_level_color(card_lvl):
        if card_lvl <= 500:
            return (255, 255, 255)  # white
        elif 501 <= card_lvl <= 1000:
            return (255, 215, 0)    # gold
        elif 1001 <= card_lvl <= 2000:
            return (255, 165, 0)    # orange
        elif 2001 <= card_lvl <= 3000:
            return (0,0,0)    # red
        else:
            return  (75, 0, 130)  # default to Indigo if level is out of expected range

    card_lvl_int = int(self.card_lvl)
    color = get_level_color(card_lvl_int)

    # Determine stroke fill based on color
    stroke_fill = (255, 255, 255) if color == (0,0,0) else (0, 0, 0)


    draw.text(lvl_sizing, f"{self.card_lvl}", color, font=lvl_font, stroke_width=1, stroke_fill=stroke_fill, align="center")
    
        
    return lvl_sizing


def paste_stars(im, star, tier):
    star_positions = [
        (230, 520), (310, 515), (380, 490), (437, 452), 
        (480, 395), (507, 325), (521, 250), (512, 170), 
        (485, 100), (430, 40)
    ]
    
    for i in range(int(tier)):
        if i >= len(star_positions):
            break  # Ensure we don't exceed available positions
        position = star_positions[i]
        im.paste(star, position, star)
        
    return im


def wrap_text(text, width):
    """
    Insert newline characters into the text at every 'width' characters.
    """
    lines = []
    for i in range(0, len(text), width):
        lines.append(text[i:i + width])
    return '\n'.join(lines)


def format_number(num):
    if num >= 1_000_000:
        return "{:.1f}M".format(num / 1_000_000)
    elif num >= 1_000:
        return "{:.1f}K".format(num / 1_000)
    else:
        return str(num)  # or just return num for a numeric value