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
        self.new_move = ""
        self.show_img = ""

        self.passive_type = list(self.abilities.keys())[0]
        self.passive_value = list(self.abilities.values())[0]
        self.price_message = ""
        self.message = ""
        self.type_message = ""

    def is_not_universe_unbound(self):
        if(self.universe != "Unbound"):
            self.show_img = db.queryUniverse({'TITLE': self.universe})['PATH']
            return True
        else:
            return False

    
    def set_element_emoji(self):
        if self.element:
            self.element = crown_utilities.set_emoji(self.element)

    
    def set_message_and_price_message(self):
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


    def is_move(self):
        move_types = ['BASIC', 'SPECIAL', 'ULTIMATE']
        if self.passive_type in move_types:
            return True
        else:
            return False
