import crown_utilities
import random


def summon_persona(player_card, battle_config, opponent_card):
    if player_card.universe == "Persona":
        dmg = player_card.damage_cal("Persona", battle_config, opponent_card)
        opponent_card.health = opponent_card.health - dmg['DMG']
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.summon_name} enhanced {player_card.name}'s next attack. {opponent_card.name} summon is disabled")
        player_card.activate_element_check(battle_config, dmg, opponent_card)
        opponent_card.usedsummon = True
        player_card.damage_dealt = player_card.damage_dealt + dmg['DMG']
    else:
        return False
    
def summon_blitz(player_card, battle_config, opponent_card):
    if player_card.universe == "Persona":
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} summoned {player_card.summon_name} to blitz!")
        dmg = player_card.damage_cal(6, battle_config, opponent_card)
        player_card.damage_done(battle_config, dmg, opponent_card)
        
    else:
        return False