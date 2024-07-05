import crown_utilities
import random


def conquerors_haki(player_card, battle_config, opponent_card, player_title):
    if player_card.universe == "One Piece" and (player_card.tier in crown_utilities.HIGH_TIER_CARDS):
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

        opponent_card.card_lvl_ap_buff = opponent_card.card_lvl_ap_buff - (100 * player_card.tier)
        if opponent_card.card_lvl_ap_buff <=0:
            opponent_card.card_lvl_ap_buff = 1
        
        title_message = ""
        
        if player_title.singularity_effect:
            resolve_health, resolve_attack_value, resolve_defense_value, title_message = player_title.singularity_handler(resolve_health, resolve_attack_value, resolve_defense_value)


        player_card.stamina = player_card.stamina + player_card.resolve_value
        player_card.health = player_card.health + resolve_health
        player_card.damage_healed = player_card.damage_healed + resolve_health
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = round(player_card.defense - resolve_defense_value)
        player_card.used_resolve = True
        player_card.usedsummon = False
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}  activated ⚡Conquerors Haki {title_message} opponent's ap reduced by {100 * player_card.tier}")
        # battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True

def armament(player_card, health_calculation, battle_config, attack_calculation, defense_calculation):
    if player_card.universe == "One Piece" and (player_card.tier in crown_utilities.MID_TIER_CARDS or player_card.tier in crown_utilities.HIGH_TIER_CARDS):
        attack_calculation = attack_calculation + attack_calculation
        defense_calculation = defense_calculation + defense_calculation
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}'s Armament Haki increases health, attack and defense [+❤️{health_calculation} | +🗡️ {attack_calculation} | +🛡️{defense_calculation}]")


def observation_haki(player_card, battle_config, opponent_card):
    if player_card.universe == "One Piece" and not player_card.haki_message:
        battle_config.turn_zero_has_happened = True
        player_card.haki_message = True
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}  Observation Haki reduces damage by 40% until first focus")





