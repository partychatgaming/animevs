import unique_traits as ut
import crown_utilities
import textwrap
import db


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

        # 
        self.resolved = False
        self.focused = False
        self.dungeon = False
        self.dungeon_card_details = ""
        self.tales_card_details = ""
        self.destiny_card_details = ""
        self.turn = 1

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
        

        self.dungeon_card_details
        
        self.pokemon_universe = False
        
        
    def is_universe_unbound(self):
        if(self.universe == "Unbound"):
            return True


    # This method will set the level buffs & apply them
    def set_card_level_buffs(self, list_of_card_levels):
        try:
            for x in list_of_card_levels:
                if x['CARD'] == self.name:
                    self.card_lvl = x['LVL']
                    self.card_exp = x['EXP']
                    self.card_lvl_ap_buff = crown_utilities.level_sync_stats(self.card_lvl, "AP")
                    self.card_lvl_attack_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
                    self.card_lvl_defense_buff = crown_utilities.level_sync_stats(self.card_lvl, "ATK_DEF")
                    self.card_lvl_hlt_buff = crown_utilities.level_sync_stats(self.card_lvl, "HLT")
            
            # applying buffs. If no buffs, adds 0
            self.max_health = self.max_health + self.card_lvl_hlt_buff
            self.health = self.health + self.card_lvl_hlt_buff
            self.attack = self.attack + self.card_lvl_attack_buff
            self.defense = self.defense + self.card_lvl_defense_buff

        except:
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


    # def set_card_details(self):
    #     if self.exclusive and not self.has_collection:
    #         self.dungeon_card_details.append(
    #             f"[{str(index)}] {universe_crest} : :mahjong: **{card['TIER']}** **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n**{level_icon}**: {str(level)} :heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")
    #     elif not self.has_collection:
    #         tales_card_details.append(
    #             f"[{str(index)}] {universe_crest} : :mahjong: **{card['TIER']}** **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n**{level_icon}**: {str(level)} :heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")
    #     elif self.has_collection:
    #         destiny_card_details.append(
    #             f"[{str(index)}] {universe_crest} : :mahjong: **{card['TIER']}** **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n**{level_icon}**: {str(level)} :heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")


    
    def get_card_index(self, list_of_cards):
        try:
            self.index = list_of_cards.index(self.name)
            return self.index
        except:
            return 0


    def set_arm_attack_swap(self, arm_type, arm_name, arm_value, arm_element=None):
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
