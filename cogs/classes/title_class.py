import db

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
    def set_title_image(self):
        if self.universe != 'Unbound':
            self.title_img = db.queryUniverse({'TITLE': self.universe})['PATH']
        
        return self.title_img


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


    def set_title_suffix(self):
        title_suffix_mapping = {'ATK': ' Flat',
            'DEF': ' Flat',
            'STAM': ' Flat',
            'HLT': ' %',
            'LIFE': '%',
            'DRAIN': ' Flat',
            'FLOG': '%',
            'WITHER': '%',
            'RAGE': '%',
            'BRACE': '%',
            'BZRK': '%',
            'CRYSTAL': '%',
            'GROWTH': ' Flat',
            'STANCE': ' Flat',
            'CONFUSE': ' Flat',
            'BLINK': ' Flat',
            'SLOW': ' Turn',
            'HASTE': ' Turn',
            'FEAR': ' Flat',
            'SOULCHAIN': ' Flat',
            'GAMBLE': ' Flat',
            'WAVE': ' Flat',
            'CREATION': '%',
            'BLAST': ' Flat',
            'DESTRUCTION': '%',
            'BASIC': ' Flat',
            'SPECIAL': ' Flat',
            'ULTIMATE': ' Flat',
            'ULTIMAX': ' Flat',
            'MANA': ' %',
            'SHIELD': ' DMG 🌐',
            'BARRIER': ' Blocks 💠',
            'PARRY': ' Counters 🔄',
            'SIPHON': ' Healing 💉'
        }
        return title_suffix_mapping[self.passive_type]
        

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
        
        return self.message