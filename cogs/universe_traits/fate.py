import crown_utilities
import random

def command_seal(player_card, battle_config, opponent_card, player_title):
    if player_card.universe == "Fate":  # Fate Trait
        # fortitude or luck is based on health
        fortitude = 0.0
        low = player_card.health - (player_card.health * .75)
        high = player_card.health - (player_card.health * .66)
        fortitude = round(random.randint(int(low), int(high)))
        # Resolve Scaling
        resolve_health = round(fortitude + (.5 * player_card.resolve_value))
        resolve_attack_value = round(
            (.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))
        resolve_defense_value = round(
            (.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))
        
        title_message = ""

        if player_title.singularity_effect:
            resolve_health, resolve_attack_value, resolve_defense_value, title_message = player_title.singularity_handler(resolve_health, resolve_attack_value, resolve_defense_value)


        player_card.stamina = player_card.stamina + player_card.resolve_value
        player_card.health = player_card.health + resolve_health
        player_card.damage_healed = player_card.damage_healed + resolve_health
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = round(player_card.defense - resolve_defense_value)
        
        damage_calculation_response = player_card.damage_cal(3, battle_config, opponent_card)
        opponent_card.health = opponent_card.health - damage_calculation_response['DMG']
        player_card.damage_dealth = player_card.damage_dealt + damage_calculation_response['DMG']
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} ♾️ resolved with their command seal {title_message}")

        # player_card.stamina = 0
        player_card.used_resolve = True
        player_card.usedsummon = False
        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True