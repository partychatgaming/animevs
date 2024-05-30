import db
import crown_utilities
import custom_logging
import textwrap
from interactions import Client, ActionRow, Button, ButtonStyle, Embed

class Trading:
    def __init__(self, merchant, buyer) -> None:
        self.merchant = merchant
        self.buyer = buyer
        self.cards = []
        self.arms = []
        self.summons = []
        self.gold = []
        self.tax = 0
        self.open = True

    def set_merchant(self, merchant):
        self.merchant = merchant

    def set_buyer(self, buyer):
        self.buyer = buyer
    
    def set_cards(self, cards):
        self.cards = cards
    
    def set_arms(self, arms):
        self.arms = arms
    
    def set_summons(self, summons):
        self.summons = summons
    
    def set_gold(self, gold):
        self.gold = gold

    def set_tax(self, tax):
        self.tax = tax

    def set_open(self, open):
        self.open = open

    def get_open(self):
        return self.open

    def get_cards(self):
        return self.cards
    
    def get_arms(self):
        return self.arms

    def get_summons(self):
        return self.summons

    def get_gold(self):
        return self.gold

    def get_tax(self):
        return self.tax

    def get_merchant(self):
        return self.merchant

    def get_buyer(self):
        return self.buyer 


    def get_trade_data(self):
        return {
            'MERCHANT': self.merchant.did,
            'BUYER': self.buyer.did,
            'CARDS': self.cards,
            'ARMS': self.arms,
            'SUMMONS': self.summons,
            'GOLD': self.gold,
            'TAX': self.tax,
            'OPEN': self.open
        }


    def add_gold(self, trader_did, amount):
        has_gold = False
        for gold in self.gold:
            if gold['DID'] == trader_did:
                new_amount = gold['AMOUNT'] + amount
                gold['AMOUNT'] = new_amount
                has_gold = True
        if not has_gold:
            self.gold.append({'DID': trader_did, 'AMOUNT': int(amount)})
        return True
                

    def subtract_gold(self, trader_did, amount):
        for gold in self.gold:
            if gold['DID'] == trader_did:
                new_amount = gold['AMOUNT'] - amount
                if new_amount < 0:
                    gold['AMOUNT'] = 0
                gold['AMOUNT'] = new_amount

        return True

    def get_query(self):
        return {"MERCHANT": str(self.merchant.did), "BUYER": str(self.buyer.did), "OPEN": True}

    def get_trade_message(self):
        trader_cards_message = []
        trade_partner_cards_message = []

        trader_arms_message = []
        trade_partner_arms_message = []

        trader_summons_message = []
        trade_partner_summons_message = []

        trader_gold_message = "0"
        trade_partner_gold_message = "0"

        for card in self.cards:
            if card['DID'] == self.merchant.did:
                trader_cards_message.append(f"{card['NAME']} [🔱{card['LVL']} / 🀄{card['TIER']}]")
            else:
                trade_partner_cards_message.append(f"{card['NAME']} [🔱{card['LVL']} / 🀄{card['TIER']}]")

        for arm in self.arms:
            if arm['DID'] == self.merchant.did:
                trader_arms_message.append(f"{arm['NAME']} [⚒️{arm['DUR']}]")
            else:
                trade_partner_arms_message.append(f"{arm['NAME']} [⚒️{arm['DUR']}]")

        for summon in self.summons:
            if summon['DID'] == self.merchant.did:
                trader_summons_message.append(f"{summon['NAME']} [LVL - {summon['LVL']}] [BOND - {summon['BOND']}]")
            else:
                trade_partner_summons_message.append(f"{summon['NAME']} [LVL - {summon['LVL']}] [BOND - {summon['BOND']}]")
        
        for gold in self.gold:
            if gold['DID'] == self.merchant.did:
                trader_gold_message = f"{gold['AMOUNT']:,}"

            else: 
                trade_partner_gold_message = f"{gold['AMOUNT']:,}"


        mcards = "\n".join(trader_cards_message) if len(trader_cards_message) > 0 else " "
        bcards = "\n".join(trade_partner_cards_message) if len(trade_partner_cards_message) > 0 else " "

        marms = "\n".join(trader_arms_message) if len(trader_arms_message) > 0 else " "
        barms = "\n".join(trade_partner_arms_message) if len(trade_partner_arms_message) > 0 else " "

        msummons = "\n".join(trader_summons_message) if len(trader_summons_message) > 0 else " "
        bsummons = "\n".join(trade_partner_summons_message) if len(trade_partner_summons_message) > 0 else " "

        embedVar = Embed(title= f"Trade Window", description=f"👨‍🏫 <@{self.merchant.did}> 🪙 ~ {trader_gold_message}\n"f"🎴 {mcards}\n"f"🦾 {marms}\n"f"🧬 {msummons}\n\n"f"🤵 <@{self.buyer.did}> 🪙 ~ {trade_partner_gold_message}\n"f"🎴 {bcards}\n"f"🦾 {barms}\n"f"🧬 {bsummons}", color=0x7289da)
        # embedVar.set_footer(text=f"🪙 Trade Tax: {self.tax:,}")

        return embedVar

