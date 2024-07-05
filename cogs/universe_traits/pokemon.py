import crown_utilities
import random


def evolutions(player_card, battle_config, player_title):
    if player_card.universe == "Kanto Region" or player_card.universe == "Johto Region" or player_card.universe == "Hoenn Region" or player_card.universe == "Sinnoh Region" or player_card.universe == "Kalos Region" or player_card.universe == "Unova Region" or player_card.universe == "Alola Region" or player_card.universe == "Galar Region":  # Pokemon Resolves
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
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = player_card.defense * 2
        player_card.used_resolve = True
        player_card.usedsummon = False

        evolution_boost = 250 * player_card.tier
        if battle_config.turn_total >= 40:
            player_card.max_health = player_card.max_health + (evolution_boost * 2)
            player_card.health = player_card.health + (evolution_boost * 2)
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} evolved into their ⚡Gigantomax Evolution gaining 1000 health {title_message}")
        elif battle_config.turn_total >= 20:
            player_card.max_health = player_card.max_health + evolution_boost
            player_card.health = player_card.health + evolution_boost
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}  evolved into their ⚡Mega Evolution gaining 500 health {title_message}")
        else:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}  evolved into their ⚡Dynamax Evolution  {title_message}")

        player_card.damage_healed = player_card.damage_healed + resolve_health + evolution_boost
        # battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True