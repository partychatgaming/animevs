import unique_traits as ut
import crown_utilities
import textwrap
import db
import random


class Card:
    def __init__(self, name, path, price, exclusive, available, is_skin, skin_for, max_health, health, max_stamina, stamina, moveset, attack, defense, type, passive, speed, universe, has_collection, tier, collection, weaknesses, resistances, repels, absorbs, immunity, gif, fpath, rname):
        self.name = name
        self.fpath= fpath
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

        # Card level & level buffs
        self.card_lvl = 0
        self.card_tier = 0
        self.card_exp = 0
        self.card_lvl_attack_buff = 0
        self.card_lvl_defense_buff = 0
        self.card_lvl_hlt_buff = 0
        self.card_lvl_ap_buff = 0

        # Battle requirements
        self.resolved = False
        self.focused = False
        self.dungeon = False
        self.dungeon_card_details = ""
        self.tales_card_details = ""
        self.destiny_card_details = ""
        self.turn = 1
        self.used_focus = False
        self.used_resolved = False
        self.enhancer_used = False
        self.summon_used = False
        self.block_used = False

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
        self.move1ap = list(self.m1.values())[0] + self.card_lvl_ap_buff
        self.move1_stamina = list(self.m1.values())[1]
        self.move1_element = list(self.m1.values())[2]
        self.move1_emoji = crown_utilities.set_emoji(self.move1_element)

        # Move 2
        self.move2 = list(self.m2.keys())[0]
        self.move2ap = list(self.m2.values())[0] + self.card_lvl_ap_buff
        self.move2_stamina = list(self.m2.values())[1]
        self.move2_element = list(self.m2.values())[2]
        self.move2_emoji = crown_utilities.set_emoji(self.move2_element)

        # Move 3
        self.move3 = list(self.m3.keys())[0]
        self.move3ap = list(self.m3.values())[0] + self.card_lvl_ap_buff
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

        # Universe Traits
        self._final_stand = False
        self._atk_chainsawman_buff = False
        self._def_chainsawman_buff = False

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
        
    def is_universe_unbound(self):
        if(self.universe == "Unbound"):
            return True


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


    def set_passive_values(self):
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

    
    def get_card_index(self, list_of_cards):
        try:
            self.index = list_of_cards.index(self.name)
            return self.index
        except:
            return 0


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
    def set_explore_bounty_and_difficulty(self):
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


        self.card_lvl_attack_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_defense_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
        self.card_lvl_ap_buff = crown_utilities.level_sync_stats(self.card_lvl, "AP")
        self.card_lvl_hlt_buff = crown_utilities.level_sync_stats(self.card_lvl, "HLT")

        if self.bounty >= 150000:
            bounty_icon = ":money_with_wings:"
        elif self.bounty >= 100000:
            bounty_icon = ":moneybag:"
        elif self.bounty >= 50000 or self.bounty <= 49999:
            bounty_icon = ":dollar:"

        self.bounty_message = f"{bounty_icon} {'{:,}'.format(self.bounty)}"
        self.battle_message = "Glory: Defeat the card and earn the card and the bounty, but if you lose you lose gold! Gold: Earn gold only!"

        self.set_card_level_buffs(None)