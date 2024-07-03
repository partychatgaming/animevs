import crown_utilities
import random

# def handle_card(card, other_card, battle_config, dmg):
#     if card.health <= 0 and card.philosopher_stone and card.universe == "Full Metal Alchemist":
#         if card.barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not dmg['SUMMON_USED']:
#             card.barrier_active = False
#             battle_config.add_to_battle_log(f"({battle_config.turn_total}) {card.name} disengaged their barrier to engage with an attack")
#         # battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {card.name} is crafting a philosphers stone!")
#         if card.health < 0:
            

#         card.damage_healed = card.damage_healed + card.health
#         card.used_resolve = True
#         card.used_focus = True
#         card._final_stand = False
#         return True
#     return False

def philosopher_stone(player_card, battle_config, dmg, opponent_card=None):
    
    if handle_card(player_card, opponent_card, battle_config, dmg):
        return True
    if handle_card(opponent_card, player_card, battle_config, dmg):
        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True
    return False


def equivalent_exchange(player_card, battle_config, attack_damage, stamina_used):
    if player_card.universe == "Full Metal Alchemist":
        if player_card.used_resolve and player_card.philospher_stone:
            healing_percent = round(((player_card.focus_count * player_card.tier) / 100) * attack_damage)
            player_card.health += healing_percent
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}'s Philosopher's stone healed them for {healing_percent} health ❤️")
        player_card.equivalent_exchange += round(stamina_used/ 2)
        player_card.universe_trait_value = player_card.equivalent_exchange
        player_card.universe_trait_value_name = "Equivalent Exchange"
        bonus_attack = player_card.equivalent_exchange * player_card.tier
        return bonus_attack

def equivalent_exchange_resolve(player_card, battle_config):
    if player_card.universe == "Full Metal Alchemist":
        if player_card.used_resolve:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} sacrificed {philosopher_stone_amount} health to craft a philosphers stone!")
            philosopher_stone_amount = player_card.equivalent_exchange * player_card.tier
            player_card.health -= philosopher_stone_amount
            if player_card.health < 0:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} crafted a philosophers stone! They are reviving with {philosopher_stone_amount} health!")
                player_card.health = philosopher_stone_amount * 2
                player_card.philospher_stone = True
        return True

