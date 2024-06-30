import crown_utilities
import random

def digivolve(player_card, battle_config, opponent_card):
    if not player_card.used_resolve and player_card.used_focus and player_card.universe == "Digimon":
        fortitude = 0.0
        low = player_card.health - (player_card.health * .75)
        high = player_card.health - (player_card.health * .66)
        fortitude = round(random.randint(int(low), int(high)))
        # Resolve Scaling
        resolve_health = round(fortitude + (.5 * player_card.resolve_value))
        resolve_attack_value = round((.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))
        resolve_defense_value = round((.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))

        player_card.stamina = player_card.stamina + player_card.resolve_value
        player_card.health = player_card.health + resolve_health
        player_card.damage_healed = player_card.damage_healed + resolve_health
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = round(player_card.defense - resolve_defense_value)
        player_card.attack = round(player_card.attack * 1.5)
        player_card.defense = round(player_card.defense * 1.5)
        player_card.used_resolve = True
        player_card.usedsummon = False
        if battle_config.turn_total <= 5:
            player_card.attack = round(player_card.attack * 2)
            player_card.defense = round(player_card.defense * 2 )
            player_card.health = player_card.health + 500
            player_card.damage_healed = player_card.damage_healed + 500
            player_card.max_health = player_card.max_health + 500
            battle_config.add_to_battle_log(f"(⚡) {player_card.name} ♾️Mega Digivolved")
        else:
            battle_config.add_to_battle_log(f"(⚡) {player_card.name} ♾️ Digivolved")
    
