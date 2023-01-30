# import db
# import crown_utilities


# class Vault:
#     def __init__(self, owner, ownerid, balance, cards, titles, arms, summons, deck, card_levels, quests, destiny, gems, storage, talismans, essence, tstorage, astorage):
#         self.owner = owner
#         self.ownerid = ownerid
#         self.balance = balance
#         self.cards = cards
#         self.titles = titles
#         self.arms = arms
#         self.summons = summons
#         self.deck = deck
#         self.card_levels = card_levels
#         self.quests = quests
#         self.destiny = destiny
#         self.gems = gems
#         self.storage = storage
#         self.talismans = talismans
#         self.essence = essence
#         self.tstorage = tstorage
#         self.astorage = astorage

#         self.list_of_cards = ""

#         self._deck_card = ""
#         self._deck_title = ""
#         self._deck_arm = ""
#         self._deck_summon = ""


#     def has_storage(self):
#         if self.storage:
#             return True
#         else:
#             return False


#     def set_list_of_cards(self):
#         cards = db.querySpecificCards(self.storage)
#         self.list_of_cards = [x for x in cards]
#         return self.list_of_cards


#     def set_deck_config(self, selected_deck):
#         try:
#             active_deck = self.deck[selected_deck]
#             self._deck_card = db.queryCard({'NAME': str(active_deck['CARD'])})
#             self._deck_title = db.queryTitle({'TITLE': str(active_deck['TITLE'])})
#             self._deck_arm = db.queryArm({'ARM': str(active_deck['ARM'])})
#             self._deck_summon = db.queryPet({'PET': str(active_deck['PET'])})
#         except:
#             print("Error setting deck config")


    
