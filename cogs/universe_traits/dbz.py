import crown_utilities
import random

def handle_card(card, other_card, battle_config, dmg):
    if card.health <= 0 and card._final_stand and card.universe == "Dragon Ball Z":
        if card.barrier_active and dmg['ELEMENT'] != "PSYCHIC" and not dmg['SUMMON_USED']:
            card.barrier_active = False
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {card.name} disengaged their barrier to engage with an attack")
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {card.name} is undergoing a transformation")
        card.health = 1 + round(.75 * (card.attack + card.defense))
        if card.health < 0:
            card.health = 100 + round(.75 * (card.base_attack + card.base_defense))
            if battle_config.is_tutorial_game_mode and not battle_config.tutorial_health_check and card.name != "Training Dummy":
                battle_config.tutorial_health_check = True
                battle_config.tutorial_messages(card,None,"HEALTH")
        card.damage_healed = card.damage_healed + card.health
        card.used_resolve = True
        card.used_focus = True
        card._final_stand = False
        return True
    return False

def final_stand(player_card, battle_config, dmg, opponent_card):
    if handle_card(player_card, opponent_card, battle_config, dmg):
        return True
    if handle_card(opponent_card, player_card, battle_config, dmg):
        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True
    return False


def saiyan_spirit(player_card, battle_config, opponent_card):
    if player_card.universe == "Dragon Ball Z":
        player_card.health = player_card.health + opponent_card.stamina + battle_config.turn_total
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}'s fighting spirit healted them for {opponent_card.stamina + battle_config.turn_total} health ❤️")



