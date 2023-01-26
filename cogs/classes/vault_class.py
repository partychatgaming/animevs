import db


class Vault:
    def __init__(self, owner, ownerid, balance, cards, titles, arms, summons, deck, card_levels, quests, destiny, gems, storage, talismans, essence, tstorage, astorage):
        self.owner = owner
        self.ownerid = ownerid
        self.balance = balance
        self.cards = cards
        self.titles = titles
        self.arms = arms
        self.summons = summons
        self.deck = deck
        self.card_levels = card_levels
        self.quests = quests
        self.destiny = destiny
        self.gems = gems
        self.storage = storage
        self.talismans = talismans
        self.essence = essence
        self.tstorage = tstorage
        self.astorage = astorage

        self.list_of_cards = ""

        

    def has_storage(self):
        if self.storage:
            return True
        else:
            return False

    def set_list_of_cards(self):
        cards = db.querySpecificCards(self.storage)
        self.list_of_cards = [x for x in cards]
        return self.list_of_cards


    
