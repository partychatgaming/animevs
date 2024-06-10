import db
import crown_utilities

class Summon:
    def __init__(self, name, universe, path, available, drop_style, abilities):
        self.name = name
        self.universe = universe
        self.path = path
        self.abilities = abilities
        self.available = available
        self.drop_style = drop_style
        self.show_img = ""
        self.is_tale_drop = False
        self.is_dungeon_drop = False
        self.is_scenario_drop = False
        self.is_boss_drop = False
        self.is_raid_drop = False

        self.passive = abilities[0]
        self.ability = list(self.passive.keys())[0]
        self.passive_value = list(self.passive.values())[0]
        self.ability_type = list(self.passive.values())[1]
        self.emoji = crown_utilities.set_emoji(self.ability_type)

        self.message = ""
        self.type_message = ""
        self.value = f"{self.emoji} {self.ability}: {str(self.passive_value)}"  
        self.explanation = f"{self.emoji} {self.ability}: {str(self.passive_value)}"  
        self.universe_crest = crown_utilities.crest_dict[self.universe]

        # For when checking for summons in player summons collection
        self.level = 0
        self.exp = 0
        self.ability_power_potential = 0
        self.ability_power = 0
        self.bond = 0
        self.bond_exp = 0
        self.exp_to_level_up = 0
        self.exp_to_bond_up = 0
        self.bond_message = ""
        self.level_message = ""
        self.dismantle_amount = 0
        self.protections = ['BARRIER','PARRY']
        
        if self.drop_style == "TALES":
            self.is_tale_drop = True
            self.drop_emoji = f"🎴"
            self.dismantle_amount = 30000
        elif self.drop_style == "DUNGEON":
            self.is_dungeon_drop = True
            self.drop_emoji = f"🔥"
            self.dismantle_amount = 100000
        elif self.drop_style == "SCENARIO":
            self.is_scenario_drop = True
            self.drop_emoji = f"🎞️"
            self.dismantle_amount = 50000
        elif self.drop_style == "BOSS":
            self.is_boss_drop = True
            self.drop_emoji = f"👹"
            self.dismantle_amount = 1000000
        elif self.drop_style == "RAID":
            self.is_raid_drop = True
            self.drop_emoji = f"💀"
            self.dismantle_amount = 1000000

    def is_not_universe_unbound(self):
        if(self.universe != "Unbound"):
            self.show_img = db.queryUniverse({'TITLE': self.universe})['PATH']
            return True
        else:
            return False


    def set_player_summon_info(self, player):
        for summon in player.summons:
            if self.name == summon['NAME']:
                self.level = summon['LVL']
                self.exp = summon['EXP']
                self.ability_power_potential = summon[self.ability]
                self.bond = summon['BOND']
                self.bond_exp = summon['BONDEXP']
                self.message = f"{self.drop_emoji} {self.name} ({self.universe_crest}) Level: {self.level} | Bond: {self.bond} | Ability: {self.ability} | Ability Power: {self.ability_power_potential}"
                self.type_message = f"{self.drop_emoji} {self.name} ({self.universe_crest}) Level: {self.level} | Bond: {self.bond} | Ability: {self.ability} | Ability Power: {self.ability_power_potential}"

                self.exp_to_bond_up = ((self.ability_power_potential * 5) * (self.bond + 1))
                if self.ability in self.protections:
                    self.exp_to_bond_up = ((self.ability_power_potential * 5) * (self.bond + 1))
                self.exp_to_level_up = (int(self.level) * 100) * (int(self.bond) + 1)
                
                if self.exp_to_level_up <= 0:
                    self.exp_to_level_up = 25
                if self.exp_to_bond_up <= 0:
                    self.exp_to_bond_up = 100
                
                self.level_message = f"*{self.exp}/{self.exp_to_level_up}*"
                self.bond_message = f"*{self.bond_exp}/{self.exp_to_bond_up}*"
                
                if self.bond == 3:
                    self.bond_message = "🌟"
                if self.level == 10:
                    self.level_message = "⭐"

                self.ability_power = ((self.bond + 1) * self.level) + ((1 + self.bond) * self.ability_power_potential)
                if self.ability in self.protections:
                    self.ability_power = (self.bond + 1) + self.ability_power_potential




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