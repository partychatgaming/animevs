import db
import crown_utilities

class Summon:
    def __init__(self, name, universe, path, abilities, available, exclusive):
        self.name = name
        self.universe = universe
        self.path = path
        self.abilities = abilities
        self.available = available
        self.exclusive = exclusive
        self.show_img = ""

        self.passive = abilities[0]
        self.passive_name = list(self.passive.keys())[0]
        self.passive_value = list(self.passive.values())[0]
        self.passive_type = list(self.passive.values())[1]

        self.message = ""
        self.type_message = ""
        self.value = ""
        self.explanation = ""
        
    def is_not_universe_unbound(self):
        if(self.universe != "Unbound"):
            self.show_img = db.queryUniverse({'TITLE': self.universe})['PATH']
            return True
        else:
            return False


    def set_messages(self):  
        if self.passive_type == 'ATK':
            self.type_message = "Attack"
            self.message = f"{self.name} is a ATK Summon"
            self.value = f"{self.passive_name}: Increase {self.type_message} by {self.passive_value}{enhancer_suffix_mapping[self.passive_type]}"
        elif self.passive_type == 'DEF':
            self.type_message = "Defense"
            self.message = f"{self.name} is a DEF Summon"
            self.value = f"{self.passive_name}: Increase {self.type_message} by {self.passive_value}{enhancer_suffix_mapping[self.passive_type]}"
        elif self.passive_type == 'STAM':
            self.type_message = "Stamina"
            self.message = f"{self.name} is a STAM Summon"
            self.value = f"{self.passive_name}: Increase {self.type_message} by {self.passive_value}{enhancer_suffix_mapping[self.passive_type]}"
        elif self.passive_type == 'HLT':
            self.type_message = "Health"
            self.message = f"{self.name} is a HLT Summon"
            self.value = f"{self.passive_name}: Increase {self.type_message} by {self.passive_value}{enhancer_suffix_mapping[self.passive_type]}"
        elif self.passive_type == 'LIFE':
            self.type_message = "of Opponents Health"
            self.message = f"{self.name} is a LIFE Summon"
            self.value = f"{self.passive_name}: Steals {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} {self.type_message}"
        elif self.passive_type == 'DRAIN':
            self.type_message = "of Opponents Stamina"
            self.message = f"{self.name} is a DRAIN Summon"
            self.value = f"{self.passive_name}: Steals {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} {self.type_message}"
        elif self.passive_type == 'FLOG':
            self.type_message = "of Opponents Attack"
            self.message = f"{self.name} is a FLOG Summon"
            self.value = f"{self.passive_name}: Steals {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} {self.type_message}"
        elif self.passive_type == 'WITHER':
            self.type_message = "of Opponents Defense"
            self.message = f"{self.name} is a WITHER Summon"
            self.value = f"{self.passive_name}: Steals {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} {self.type_message}"
        elif self.passive_type == 'RAGE':
            self.type_message = f"Defense to gain {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} AP"
            self.message = f"{self.name} is a RAGE Summon"
            self.value = f"{self.passive_name}: Sacrifice {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} {self.type_message}"
        elif self.passive_type == 'BRACE':    
            self.type_message = f"Attack to gain {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} AP"        
            self.message = f"{self.name} is a BRACE Summon"
            self.value = f"{self.passive_name}: Sacrifice {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} {self.type_message}"
        elif self.passive_type == 'BZRK':    
            self.type_message = f"Health to gain {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} Attack"        
            self.message = f"{self.name} is a BZRK Summon"
            self.value = f"{self.passive_name}: Sacrifice {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} {self.type_message}"
        elif self.passive_type == 'CRYSTAL':    
            self.type_message = f"Health to gain {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} Defense"        
            self.message = f"{self.name} is a CRYSTAL Summon"
            self.value = f"{self.passive_name}: Sacrifice {self.passive_value}{enhancer_suffix_mapping[self.passive_type]} {self.type_message}"
        elif self.passive_type == 'GROWTH':    
            self.type_message = f"Max Health to gain {round(self.passive_value * .5)}{enhancer_suffix_mapping[self.passive_type]} Attack, Defense, and AP"      
            self.message = f"{self.name} is a GROWTH Summon"
            self.value = f"{self.passive_name}: Sacrifice 10% {self.type_message}"
        elif self.passive_type == 'STANCE':
            self.type_message = "Attack and Defense, Increase"
            self.message = f"{self.name} is a STANCE Summon"
            self.value = f"{self.passive_name}: Swap {self.type_message} Defense by {self.passive_value}"
        elif self.passive_type == 'CONFUSE':
            self.type_message = "Opponent Attack And Defense, Decrease Opponent"
            self.message = f"{self.name} is a CONFUSE Summon"
            self.value = f"{self.passive_name}: Swap {self.type_message} Defense by {self.passive_value}"
        elif self.passive_type == 'BLINK':
            self.type_message = "Decrease Your Stamina, Increase Opponent Stamina"
            self.message = f"{self.name} is a BLINK Summon"
            self.value = f"{self.passive_name}: {self.type_message} by {self.passive_value}"
        elif self.passive_type == 'SLOW':
            self.type_message = "Decrease Your Stamina by"
            self.message = f"{self.name} is a SLOW Summon"
            self.value = f"{self.passive_name}: {self.type_message} by {self.passive_value}, Swap Stamina with Opponent"
        elif self.passive_type == 'HASTE':
            self.type_message = "Increase Opponent Stamina by"
            self.message = f"{self.name} is a HASTE Summon"
            self.value = f"{self.passive_name}: {self.type_message} by {self.passive_value}, Swap Stamina with Opponent"
        elif self.passive_type == 'SOULCHAIN':
            self.type_message = "Stamina"
            self.message = f"{self.name} is a SOULCHAIN Summon"
            self.value = f"{self.passive_name}: Set both players {self.type_message} equal to {self.passive_value}"
        elif self.passive_type == 'FEAR':
            self.type_message = f"Max Health to reduce {round(self.passive_value * .5)}{enhancer_suffix_mapping[self.passive_type]} Opponent Attack, Defense, and AP"
            self.message = f"{self.name} is a FEAR Summon"
            self.value = f"{self.passive_name}: Sacrifice 10% {self.type_message}"
        elif self.passive_type == 'GAMBLE':
            self.type_message = "Health"
            self.message = f"{self.name} is a GAMBLE Summon"
            self.value = f"{self.passive_name}: Set both players {self.type_message} equal to {self.passive_value}"
        elif self.passive_type == 'BLAST':
            self.type_message = "Deals Increasing AP * Turn Count Damage "
            self.message = f"{self.name} is a BLAST Summon"
            self.value = f"{self.passive_name}: {self.type_message} starting at {self.passive_value}"
        elif self.passive_type == 'WAVE':
            self.type_message = "Deals Decreasing AP / Turn Count Damage"
            self.message = f"{self.name} is a WAVE Summon"
            self.value = f"{self.passive_name}: {self.type_message} starting at {self.passive_value}"
        elif self.passive_type == 'DESTRUCTION':
            self.type_message = "Destroys Increasing AP * Turn Count Max Health"
            self.message = f"{self.name} is a DESTRUCTION Summon"
            self.value = f"{self.passive_name}: {self.type_message} starting at {self.passive_value}"
        elif self.passive_type == 'CREATION':
            self.type_message = "Grants Decreasing AP / Turn Count Max Health"
            self.message = f"{self.name} is a CREATION Summon"
            self.value = f"{self.passive_name}: {self.type_message} starting at {self.passive_value}"

        self.explanation = f"{self.passive_type}: {enhancer_mapping[self.passive_type]}"  


enhancer_mapping = {'ATK': 'Increase Attack %',
'DEF': 'Increase Defense %',
'STAM': 'Increase Stamina',
'HLT': 'Heal yourself or companion',
'LIFE': 'Steal Health from Opponent',
'DRAIN': 'Drain Stamina from Opponent',
'FLOG': 'Steal Attack from Opponent',
'WITHER': 'Steal Defense from Opponent',
'RAGE': 'Lose Defense, Increase Attack',
'BRACE': 'Lose Attack, Increase Defense',
'BZRK': 'Lose Health, Increase Attack',
'CRYSTAL': 'Lose Health, Increase Defense',
'GROWTH': 'Lose Health, Increase Attack & Defense',
'STANCE': 'Swap your Attack & Defense, Increase Attack',
'CONFUSE': 'Swap Opponent Attack & Defense, Decrease Opponent Defense',
'BLINK': 'Decrease your  Stamina, Increase Target Stamina',
'SLOW': 'Decrease Opponent Stamina, Swap Stamina with Opponent',
'HASTE': ' Increase your Stamina, Swap Stamina with Opponent',
'FEAR': 'Decrease your Health, Decrease Opponent Attack and Defense',
'SOULCHAIN': 'You and Your Opponent Stamina Link',
'GAMBLE': 'You and Your Opponent Health Link',
'WAVE': 'Deal Damage, Decreases over time',
'CREATION': 'Heals you, Decreases over time',
'BLAST': 'Deals Damage, Increases over time',
'DESTRUCTION': 'Decreases Opponent Max Health, Increases over time',
'BASIC': 'Increase Basic Attack AP',
'SPECIAL': 'Increase Special Attack AP',
'ULTIMATE': 'Increase Ultimate Attack AP',
'ULTIMAX': 'Increase All AP Values',
'MANA': 'Increase Enchancer AP',
'SHIELD': 'Blocks Incoming DMG, until broken',
'BARRIER': 'Nullifies Incoming Attacks, until broken',
'PARRY': 'Returns 25% Damage, until broken',
'SIPHON': 'Heal for 10% DMG inflicted + AP'
}


enhancer_suffix_mapping = {'ATK': '%',
'DEF': '%',
'STAM': ' Flat',
'HLT': '%',
'LIFE': '%',
'DRAIN': ' Flat',
'FLOG': '%',
'WITHER': '%',
'RAGE': '%',
'BRACE': '%',
'BZRK': '%',
'CRYSTAL': '%',
'GROWTH': '%',
'STANCE': ' Flat',
'CONFUSE': ' Flat',
'BLINK': ' Flat',
'SLOW': ' Flat',
'HASTE': ' Flat',
'FEAR': '%',
'SOULCHAIN': ' Flat',
'GAMBLE': ' Flat',
'WAVE': ' Flat',
'CREATION': ' Flat',
'BLAST': ' Flat',
'DESTRUCTION': ' Flat',
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