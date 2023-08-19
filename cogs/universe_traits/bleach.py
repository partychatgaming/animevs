import crown_utilities
import random

def bankai(player_card, battle_config, player_title):
    if player_card.universe == "Bleach":  # Bleach Trait
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
        player_card.attack = round((player_card.attack + (2 * resolve_attack_value))* 2)
        player_card.defense = round(player_card.defense - resolve_defense_value)
        # if player_card.defense >= 120:
        # # player_card.defense = 120
        player_card.used_resolve = True
        player_card.usedsummon = False
        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{player_card.name}** 🩸 Resolved: Bankai!{title_message}")

        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True


def spiritual_pressure(player_card, battle_config, opponent_card):
    if player_card.universe == "Bleach":
        dmg = player_card.damage_cal(1, battle_config, opponent_card)
        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{player_card.name}** Exerted their 🩸 Energyual Pressure Executing a Basic Attack!")
        if player_card.universe == "One Piece" and (player_card.name_tier in crown_utilities.LOW_TIER_CARDS or player_card.name_tier in crown_utilities.MID_TIER_CARDS or player_card.name_tier in crown_utilities.HIGH_TIER_CARDS):
            if player_card.focus_count == 0:
                dmg['DMG'] = dmg['DMG'] * .6
        
        player_card.activate_element_check(battle_config, dmg, opponent_card)


