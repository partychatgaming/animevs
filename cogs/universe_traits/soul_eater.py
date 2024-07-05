import crown_utilities
import random


def soul_eater(player_card, battle_config, opponent_card):
    if player_card.universe == "Soul Eater":
        dmg = player_card.damage_cal(6, battle_config, opponent_card)
        opponent_card.health = opponent_card.health - dmg['DMG']
        summon_buff = 50
        if player_card.summon_universe == "Soul Eater" and player_card.summon_type not in crown_utilities.protections_list:
            summon_buff = round(dmg['DMG'] * 0.50)
        player_card.soul_resonance_amount += summon_buff
        if not player_card.used_resolve:
            player_card.universe_trait_value = player_card.soul_resonance_amount
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} & {player_card.summon_name} ate {summon_buff:,} souls. [{player_card.soul_resonance_amount} Soul Resonance]")
        player_card.activate_element_check(battle_config, dmg, opponent_card)
        player_card.damage_dealt = player_card.damage_dealt + dmg['DMG']
        player_card.soul_resonance = False
    else:
        return False
    
def soul_resonance(player_card, battle_config, health, attack, defense, title):
    if player_card.universe == "Soul Eater":
        health_gained = health + player_card.soul_resonance_amount
        attack_gained = attack + player_card.soul_resonance_amount
        defense_gained = defense + player_card.soul_resonance_amount

        player_card.health += player_card.soul_resonance_amount
        player_card.arbitrary_ap_buff += player_card.soul_resonance_amount
        player_card.summon_power += player_card.soul_resonance_amount
        player_card.universe_trait_value = "Spent"
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} & {player_card.summon_name} activated ⚡soul resonance. {title} [+❤️{health_gained} | +🗡️ {attack_gained} | --🛡️{defense_gained}]")
        return True
    else:
        return False
    
def meister(player_card, dmg):
    if player_card.universe == "Soul Eater":
        summon_buff = 50
        if player_card.summon_universe == "Soul Eater" and player_card.summon_type not in crown_utilities.protections_list:
            summon_buff = round(dmg['DMG'] * 0.50)
        player_card.soul_resonance_amount += summon_buff
        if not player_card.used_resolve:
            player_card.universe_trait_value = player_card.soul_resonance_amount