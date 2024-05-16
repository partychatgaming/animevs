import crown_utilities
import random


def substitution_jutsu(player_card, opponent_card, dmg, battle_config):
    if opponent_card.universe == "Naruto" and opponent_card.stamina < 10:
        stored_damage = round(dmg['DMG'])
        opponent_card.naruto_heal_buff = opponent_card.naruto_heal_buff + stored_damage
        opponent_card.health = opponent_card.health 

        if player_card.barrier_active and dmg['ELEMENT'] != "PSYCHIC":
            if not dmg['SUMMON_USED']:
                player_card.barrier_active = False
                player_card._barrier_value = 0
                player_card._arm_message = ""
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} disengaged their barrier to engage with an attack")
                player_card.decrease_solo_leveling_temp_values('BARRIER', opponent_card, battle_config)
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {opponent_card.name} substitution jutsu")
        if not opponent_card.used_resolve:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {stored_damage} hashira cells was stored and {opponent_card.naruto_heal_buff} is stored in total")

        return True
    else:
        return False

def hashirama_cells(player_card, battle_config, player_title):
    if player_card.universe == "Naruto":
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

        if player_title.singularity_effect:
            resolve_health, resolve_attack_value, resolve_defense_value, title_message = player_title.singularity_handler(resolve_health, resolve_attack_value, resolve_defense_value)

        player_card.stamina = player_card.stamina + player_card.resolve_value
        player_card.health = player_card.health + resolve_health
        player_card.health = player_card.health + player_card.naruto_heal_buff
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = round(player_card.defense - resolve_defense_value)

        player_card.damage_healed = player_card.damage_healed + resolve_health + player_card.naruto_heal_buff
        
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 Stored hashira cells healed {player_card.name} for {player_card.naruto_heal_buff} health")

        player_card.used_resolve = True
        player_card.usedsummon = False

        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True