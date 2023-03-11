import db
import crown_utilities

class Arm:
    def __init__(self, name, universe, price, abilities, exclusive, available, element=None):
        self.name = name
        self.universe = universe
        self.price = price
        self.abilities = abilities[0]
        self.exclusive = exclusive
        self.available = available
        self.element = element
        self.element_emoji = ""
        self.new_move = ""
        self.show_img = ""

        self.passive_type = list(self.abilities.keys())[0]
        self.passive_value = list(self.abilities.values())[0]
        self.price_message = ""
        self.message = ""
        self.type_message = ""
        self.durability = 0
        self.durability_message = "⚒️ 100"

        self.arm_message = f"⚠️ |  {self.name}: {self.durability}"

        self.pokemon_arm = False
        if self.element:
            self.element_emoji = crown_utilities.set_emoji(self.element)
        
        if(self.universe != "Unbound"):
            self.show_img = db.queryUniverse({'TITLE': self.universe})['PATH']

    
        if self.exclusive:
            self.price_message = "_Priceless_"
        else:
            self.price_message = f"_Shop & Drop_"

        if self.passive_type == 'BASIC':
            self.type_message = 'Basic'
            self.message =f"{self.name} is a basic attack arm"
        elif self.passive_type == 'SPECIAL':
            self.type_message = 'Special'
            self.message =f"{self.name} is a special attack arm"
        elif self.passive_type == 'ULTIMATE':
            self.type_message = 'Ultimate'
            self.message =f"{self.name} is an ultimate attack arm"
        elif self.passive_type == 'ULTIMAX':
            self.type_message = 'All AP'
            self.message =f"{self.name} is a ULTIMAX arm"
        elif self.passive_type == 'SHIELD':
            self.type_message = 'Shield'
            self.message =f"{self.name} is a SHIELD arm"
        elif self.passive_type == 'BARRIER':
            self.type_message = 'Barrier'
            self.message =f"{self.name} is an BARRIER arm"
        elif self.passive_type == 'PARRY':
            self.type_message = 'Parry'
            self.message =f"{self.name} is a PARRY arm"
        elif self.passive_type == 'MANA':
            self.type_message = 'Mana'
            self.message =f"{self.name} is a MANA arm"
        elif self.passive_type == 'SIPHON':
            self.type_message = 'Siphon'
            self.message =f"{self.name} is a SIPHON arm"

        if self.universe in crown_utilities.pokemon_universes:
            self.pokemon_arm = True
        if self.element:
            self.element_ability = crown_utilities.element_mapping[self.element]



    def is_move(self):
        if self.passive_type in move_types:
            return True
        else:
            return False


    def set_durability(self, equipped_arm, list_of_arms):
        base_names = ['Reborn Stock', 'Stock', 'Deadgun', 'Glaive', 'Kings Glaive', 'Legendary Weapon']
        for a in list_of_arms:
            if a['ARM'] == equipped_arm and a['ARM'] in base_names:
                self.durability = f""
            elif a['ARM'] == equipped_arm and a['ARM'] not in base_names:
                self.durability_message = f"⚒️ {a['DUR']}"
                self.durability = a['DUR']
        
        return self.durability_message


    def set_arm_message(self, performance_mode, card_universe):
        if self.passive_type in move_types:
            arm_emoji = crown_utilities.set_emoji(self.element)
            if performance_mode:
                self.arm_message = f'{arm_emoji} | {self.name}: {self.passive_type.title()} Attack: {self.passive_value} | {self.durability}'
            else:
                self.arm_message = f'{arm_emoji} | {self.name}: {self.durability}'

        if self.universe == "Unbound" or card_universe == "Crown Rift Slayers":
            armicon = "👑"
            if performance_mode:
                self.arm_message = f'👑 | {self.name}: {self.passive_type} {self.passive_value}{crown_utilities.enhancer_suffix_mapping[self.passive_type]} {self.durability}'
            else:
                self.arm_message = f'👑 | {self.name}: {self.durability}'

        elif self.universe == card_universe or (card_universe in crown_utilities.pokemon_universes and self.pokemon_arm==True):
            armicon = "🦾"
            if performance_mode:
                self.arm_message = f'🦾 | {self.name}: {self.passive_type} {self.passive_value}{crown_utilities.enhancer_suffix_mapping[self.passive_type]} {self.durability}'
            else:
                self.arm_message = f'🦾 | {self.name}: {self.durability}'
                
        else:
            armicon = "⚠️"
            if performance_mode:
                self.arm_message = f'⚠️ | {self.name}: {self.passive_type} {self.passive_value}{crown_utilities.enhancer_suffix_mapping[self.passive_type]} {self.durability}'
            else:
                self.arm_message = f'⚠️ | {self.name}: {self.durability}'


move_types = ['BASIC', 'SPECIAL', 'ULTIMATE']