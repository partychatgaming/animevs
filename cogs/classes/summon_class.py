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
        self.emoji = crown_utilities.set_emoji(self.passive_type)

        self.message = ""
        self.type_message = ""
        self.value = f"{self.emoji} {self.passive_name}: {str(self.passive_value)}"  
        self.explanation = f"{self.emoji} {self.passive_name}: {str(self.passive_value)}"  
        
    def is_not_universe_unbound(self):
        if(self.universe != "Unbound"):
            self.show_img = db.queryUniverse({'TITLE': self.universe})['PATH']
            return True
        else:
            return False


    # def set_messages(self):  
    #     self.value = f"{self.emoji} {self.passive_name}: {str(self.passive_value)}"  
    #     self.explanation = f"{self.emoji} {self.passive_name}: {str(self.passive_value)}"  


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