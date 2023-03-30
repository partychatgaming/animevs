import db
import crown_utilities

class Title:
    def __init__(self, title, universe, price, exclusive, available, abilities):
        self.name = title
        self.universe = universe
        self.price = price
        self.exclusive = exclusive
        self.available = available
        self.abilities = abilities
        self.title_img = ""

        self.passive = abilities[0]
        self.passive_type = list(self.passive.keys())[0]
        self.passive_value = list(self.passive.values())[0]

        self.price_message = ""
        self.type_message = ""
        self.type2_message = ""
        self.message = ""
        self.pokemon_title = False
        self.active_message_sent = False
        self.region_trait = False
        self.title_active = False

        self.title_message = f"⚠️ | {self.name} ~ INEFFECTIVE"
        if self.universe in crown_utilities.pokemon_universes:
            self.pokemon_title = True
        self.title_icon = "⚠️"

    def set_title_image(self):
        if self.universe != 'Unbound':
            self.title_img = db.queryUniverse({'TITLE': self.universe})['PATH']
        
        return self.title_img


    def set_pokemon_title(self):
        if self.universe in crown_utilities.pokemon_universes:
            self.pokemon_title = True


    def set_type_message_and_price_message(self):
            if self.exclusive:
                self.price_message = "_Priceless_"
            else:
                self.price_message = f"_Shop & Drop_"

            self.type2_message = " "
            if self.passive_type == 'ATK':
                self.type_message = "Attack"
                message=f"{self.name} is an ATK title"
            elif self.passive_type == 'DEF':
                self.type_message = "Defense"
                message=f"{self.name} is a DEF title"
            elif self.passive_type == 'STAM':
                self.type_message = "Stamina"
                message=f"{self.name} is a STAM title"
            elif self.passive_type == 'HLT':
                self.type_message = "Health"
                message=f"{self.name} is a HLT title"
            elif self.passive_type == 'LIFE':
                self.type_message = "Health"
                message=f"{self.name} is a LIFE title"
            elif self.passive_type == 'DRAIN':
                self.type_message = "Stamina"
                message=f"{self.name} is a DRAIN title"
            elif self.passive_type == 'FLOG':
                self.type_message = "Attack"
                message=f"{self.name} is a FLOG title"
            elif self.passive_type == 'WITHER':
                self.type_message = "Defense"
                message=f"{self.name} is a WITHER title"
            elif self.passive_type == 'RAGE':
                self.type_message = "Defense gain Attack"
                message=f"{self.name} is a RAGE title"
            elif self.passive_type == 'BRACE':    
                self.type_message = "Attack gain AP"        
                message=f"{self.name} is a BRACE title"
            elif self.passive_type == 'BZRK':    
                self.type_message = "Health gain Attack"        
                message=f"{self.name} is a BZRK title"
            elif self.passive_type == 'CRYSTAL':    
                self.type_message = "Health gain Defense"        
                message=f"{self.name} is a CRYSTAL title"
            elif self.passive_type == 'GROWTH':    
                self.type_message = "Max Health gain Attack and Defense"        
                message=f"{self.name} is a GROWTH title"
            elif self.passive_type == 'STANCE':
                self.type_message = "Attack and Defense increase"
                message=f"{self.name} is a STANCE title"
            elif self.passive_type == 'CONFUSE':
                self.type_message = "Opponent Attack And Defense decrease Opponent"
                message=f"{self.name} is a CONFUSE title"
            elif self.passive_type == 'BLINK':
                self.type_message = "Decrease Stamina"
                self.type2_message ="Increase Target Stamina"
                message=f"{self.name} is a BLINK title"
            elif self.passive_type == 'SLOW':
                self.type_message = "Decrease Turn Count"
                self.type2_message = "Decrease Stamina"
                message=f"{self.name} is a SLOW title"
            elif self.passive_type == 'HASTE':
                self.type_message = "Increase Turn Count"
                self.type2_message = "Decrease Opponent Stamina"
                message=f"{self.name} is a HASTE title" 
            elif self.passive_type == 'SOULCHAIN':
                self.type_message = "Stamina Regen"
                message=f"{self.name} is a SOULCHAIN title"
            elif self.passive_type == 'FEAR':
                self.type_message = "Max Health reduce Opponent Attack and Defense"
                message=f"{self.name} is a FEAR title"
            elif self.passive_type == 'GAMBLE':
                self.type_message = "Health Regen "
                message=f"{self.name} is a GAMBLE title" 
            elif self.passive_type == 'CREATION':
                self.type_message = "Increase Max Health"
                message=f"{self.name} is a GAMBLE title" 
            elif self.passive_type == 'DESTRUCTION':
                self.type_message = "Decrease Opponent Max Health "
                message=f"{self.name} is a DESTRUCTION title" 
            elif self.passive_type == 'BLAST':
                self.type_message = "Deal True Damage "
                message=f"{self.name} is a BLAST title" 
            elif self.passive_type == 'WAVE':
                self.type_message = "Deal True Damage"
                message=f"{self.name} is a WAVE title" 


    def set_title_suffix(self):
        title_suffix_mapping = {'ATK': '',
            'DEF': '',
            'STAM': '',
            'HLT': ' %',
            'LIFE': '%',
            'DRAIN': '',
            'FLOG': '%',
            'WITHER': '%',
            'RAGE': '%',
            'BRACE': '%',
            'BZRK': '%',
            'CRYSTAL': '%',
            'GROWTH': '',
            'STANCE': '',
            'CONFUSE': '',
            'BLINK': '',
            'SLOW': ' Turn',
            'HASTE': ' Turn',
            'FEAR': '',
            'SOULCHAIN': '',
            'GAMBLE': '',
            'WAVE': '',
            'CREATION': '%',
            'BLAST': '',
            'DESTRUCTION': '%',
            'BASIC': '',
            'SPECIAL': '',
            'ULTIMATE': '',
            'ULTIMAX': '',
            'MANA': ' %',
            'SHIELD': ' DMG 🌐',
            'BARRIER': ' Blocks 💠',
            'PARRY': ' Counters 🔄',
            'SIPHON': ' Healing 💉'
        }
        return title_suffix_mapping[self.passive_type]
        

    def set_title_message(self, performance_mode, card_universe):
        try:
            if self.universe == "Unbound" or (card_universe in crown_utilities.pokemon_universes) or card_universe == "Crown Rift Awakening":
                if performance_mode:
                    self.title_message = f"👑 | {self.name}: {self.passive_type} {self.passive_value}{crown_utilities.title_enhancer_suffix_mapping[self.passive_type]}"
                else:
                    self.title_message = f"👑 | {self.name}" 

            elif self.universe == card_universe or (card_universe in crown_utilities.pokemon_universes and self.pokemon_title==True):
                if performance_mode:
                    self.title_message = f"🎗️ | {self.name}: {self.passive_type} {self.passive_value}{crown_utilities.title_enhancer_suffix_mapping[self.passive_type]}"
                else:
                    self.title_message = f"🎗️ | {self.name}"
                        
        except:
            print("error setting title message")
            
    def get_title_icon(self, card_universe):
        try:
            if self.universe == "Unbound" or (card_universe in crown_utilities.pokemon_universes) or card_universe == "Crown Rift Awakening":
                return "👑" 

            elif self.universe == card_universe or (card_universe in crown_utilities.pokemon_universes and self.pokemon_title==True):
                return "🎗️"
            else:
                return self.title_icon
                        
        except:
            print("error setting title message")


    def set_title_embed_message(self):
        if self.passive_type == "ATK" or self.passive_type == "DEF" or self.passive_type == "HLT" or self.passive_type == "STAM":
            self.message = f"On your turn, Increases **{self.type_message}** by **{self.passive_value}{self.set_title_suffix()}**"
        
        elif self.passive_type == "FLOG" or self.passive_type == "WITHER" or self.passive_type == "LIFE" or self.passive_type == "DRAIN":
            self.message = f"On your turn, Steals **{self.passive_value}{self.set_title_suffix()} {self.type_message}**"
        
        elif self.passive_type == "RAGE" or self.passive_type == "BRACE" or self.passive_type == "BZRK" or self.passive_type == "CRYSTAL" or self.passive_type == "GROWTH" or self.passive_type == "FEAR":
            self.message = f"On your turn, Sacrifice **{self.passive_value}{self.set_title_suffix()} {self.type_message}**"
        
        elif self.passive_type == "STANCE" or self.passive_type == "CONFUSE":
            self.message = f"On your turn, Swap {self.type_message} Defense by **{self.passive_value}**"
            self.message = value=f"On your turn, **{self.type_message}** by **{self.passive_value}**, **{self.type2_message}** by **{self.passive_value}**"
        
        elif self.passive_type == "SLOW" or self.passive_type == "HASTE":
            self.message = f"On your turn, **{self.type_message}** by **{self.passive_value}**"
        
        elif self.passive_type == "SOULCHAIN" or self.passive_type == "GAMBLE":
            self.message = f"During Focus, **{self.type_message}** equal **{self.passive_value}**"
            
        elif self.passive_type == "BLAST" or self.passive_type == "WAVE":
            self.message = f"On your turn, **{self.type_message}** equal to **{self.passive_value}**"
            
        elif self.passive_type == "CREATION" or self.passive_type == "DESTRUCTION":
            self.message = f"On your turn, **{self.type_message}** by **{self.passive_value}{self.set_title_suffix()}**"
        
        return self.message
    
    def title_active_check(self, player_card):
        if self.universe == "Unbound":
            self.title_active = True
            return True
        elif player_card.universe == "Crown Rift Awakening":
            self.title_active = True
            return True
        elif (self.universe in crown_utilities.pokemon_universes and player_card.universe in crown_utilities.pokemon_universes):
            self.region_trait = True
            self.title_active = True
            return True
        elif self.universe == player_card.universe:
            self.title_active = True
            return True
        else:
            self.title_active = False
            return False
            
             


    def activate_title_passive(self, battle, player1_card, player2_card, player3_card=None):
        try:
            active = self.title_active_check(player1_card)
            if not active:
                if not self.active_message_sent:
                    self.active_message_sent = True
                    battle.add_to_battle_log(f"(**⚠️**) **Titleless** : {player1_card.name} cannot equip  **{self.name}**")
                return
            if self.passive_type:
                if self.passive_type == "HLT":
                    if player1_card.max_health > player1_card.health + ((self.passive_value / 100) * player1_card.health):
                        player1_card.health = round(player1_card.health + ((self.passive_value / 100) * player1_card.health))
                    else:
                        player1_card.health = round(player1_card.health + (player2_card.max_health - player2_card.health))
                    if player1_card.health >= player1_card.max_health:
                        player1_card.health = player1_card.max_health
                if self.passive_type == "LIFE":
                    if player1_card.max_health > (player1_card.health + ((self.passive_value / 100) * player2_card.health)):
                        player2_card.health = round(player2_card.health - ((self.passive_value / 100) * player2_card.health))
                        player1_card.health = round(player1_card.health + ((self.passive_value / 100) * player2_card.health))
                        player1_card.damage_healed = round(player1_card.damage_healed + ((self.passive_value / 100) * player2_card.health))
                        player1_card.damage_dealt = round(player1_card.damage_dealt + ((self.passive_value / 100) * player2_card.health))

                if self.passive_type == "ATK":
                    player1_card.attack = player1_card.attack + self.passive_value
                if self.passive_type == "DEF":
                    player1_card.defense = player1_card.defense + self.passive_value
                if self.passive_type == "STAM":
                    if player1_card.stamina > 15:
                        player1_card.stamina = player1_card.stamina + self.passive_value
                if self.passive_type == "DRAIN":
                    if player2_card.stamina > 15:
                        player2_card.stamina = player2_card.stamina - self.passive_value
                        player1_card.stamina = player1_card.stamina + self.passive_value
                if self.passive_type == "FLOG":
                    player2_card.attack = round(player2_card.attack - ((self.passive_value / 100) * player2_card.attack))
                    player1_card.attack = round(player1_card.attack + ((self.passive_value / 100) * player2_card.attack))
                if self.passive_type == "WITHER":
                    player2_card.defense = round(player2_card.defense - ((self.passive_value / 100) * player2_card.defense))
                    player1_card.defense = round(player1_card.defense + ((self.passive_value / 100) * player2_card.defense))
                if self.passive_type == "RAGE":
                    player1_card.defense = round(player1_card.defense - ((self.passive_value / 100) * player1_card.defense))
                    player1_card.card_lvl_ap_buff = round(player1_card.card_lvl_ap_buff + ((self.passive_value / 100) * player1_card.defense))
                if self.passive_type == "BRACE":
                    player1_card.card_lvl_ap_buff = round(player1_card.card_lvl_ap_buff + ((self.passive_value / 100) * player1_card.attack))
                    player1_card.attack = round(player1_card.attack - ((self.passive_value / 100) * player1_card.attack))
                if self.passive_type == "BZRK":
                    player1_card.health = round(player1_card.health - ((self.passive_value / 100) * player1_card.health))
                    player1_card.attack = round(player1_card.attack + ((self.passive_value / 100) * player1_card.health))
                if self.passive_type == "CRYSTAL":
                    player1_card.health = round(player1_card.health - ((self.passive_value / 100) * player1_card.health))
                    player1_card.defense = round(player1_card.defense + ((self.passive_value / 100) * player1_card.health))
                if self.passive_type == "FEAR":
                    if player1_card.universe != "Chainsawman":
                        player1_card.max_health = player1_card.max_health - (player1_card.max_health * .03)
                        if player1_card.health > player1_card.max_health:
                            player1_card.health = player1_card.max_health
                    player2_card.defense = player2_card.defense - self.passive_value
                    player2_card.attack = player2_card.attack - self.passive_value
                    player2_card.card_lvl_ap_buff = player2_card.card_lvl_ap_buff - self.passive_value
                    if player2_card.attack <= 25:
                        player2_card.attack = 25
                    if player2_card.defense <= 25:
                        player2_card.defense = 25
                    if player2_card.card_lvl_ap_buff <= 0:
                        player2_card.card_lvl_ap_buff = 1
                if self.passive_type == "GROWTH":
                    player1_card.max_health = player1_card.max_health - (player1_card.max_health * .03)
                    if player1_card.health > player1_card.max_health:
                        player1_card.health = player1_card.max_health
                    player1_card.defense = player1_card.defense + self.passive_value
                    player1_card.attack = player1_card.attack + self.passive_value
                    player1_card.card_lvl_ap_buff = player1_card.card_lvl_ap_buff + self.passive_value
                if self.passive_type == "SLOW":
                    if battle.turn_total != 0:
                        battle.turn_total = battle.turn_total - self.passive_value
                        if battle.turn_total <= 0:
                            battle.turn_total = 0
                if self.passive_type == "HASTE":
                    battle.turn_total = battle.turn_total + self.passive_value
                if self.passive_type == "STANCE":
                    tempattack = player1_card.attack + self.passive_value
                    player1_card.attack = player1_card.defense
                    player1_card.defense = tempattack
                if self.passive_type == "CONFUSE":
                    tempattack = player2_card.attack - self.passive_value
                    player2_card.attack = player2_card.defense
                    player2_card.defense = tempattack
                if self.passive_type == "BLINK":
                    player1_card.stamina = player1_card.stamina - self.passive_value
                    if player2_card.stamina >=10:
                        player2_card.stamina = player2_card.stamina + self.passive_value
                if self.passive_type == "CREATION":
                    player1_card.max_health = round(round(player1_card.max_health + ((self.passive_value / 100) * player1_card.max_health)))
                    player1_card.damage_healed = round(player1_card.damage_healed + ((self.passive_value / 100) * player1_card.max_health))
                if self.passive_type == "DESTRUCTION":
                    player2_card.max_health = round(player2_card.max_health - ((self.passive_value / 100) * player2_card.max_health))
                    player1_card.damage_dealt = round(player1_card.damage_dealt + ((self.passive_value / 100) * player2_card.max_health))
                if self.passive_type == "BLAST":
                    player2_card.health = round(player2_card.health - self.passive_value)
                    player1_card.damage_dealt = round(player1_card.damage_dealt + self.passive_value)
                if self.passive_type == "WAVE":
                    if battle.turn_total % 10 == 0:
                        player2_card.health = round(player2_card.health - 100)
                        player1_card.damage_dealt = player1_card.damage_dealt + 100
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

