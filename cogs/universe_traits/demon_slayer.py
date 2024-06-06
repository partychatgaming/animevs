import crown_utilities
import random

def total_concentration_breathing(player_card, battle_config, player_title, opponent_card):
    if player_card.universe == "Demon Slayer": 
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
        if opponent_card.attack > player_card.attack:
            player_card.attack = opponent_card.attack + (250 * player_card.tier)
        if opponent_card.defense > player_card.defense:
            player_card.defense = opponent_card.defense + (250 * player_card.tier)
        player_card.used_resolve = True
        player_card.usedsummon = False

        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} resolved with their total concentration breathing {title_message}")
        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True

def activate_demon_slayer_trait(player_card, battle_config, opponent_card):
    if player_card.universe == "Demon Slayer" and not player_card.breathing_message:
        battle_config.turn_zero_has_happened = True
        player_card.breathing_message = True
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} total concentration breathing increased their health by {round(opponent_card.health * .60):,}")
        player_card.health = round(player_card.health + (opponent_card.health * .60))
        player_card.max_health = round(player_card.max_health + (opponent_card.health *.60))





