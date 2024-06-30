import crown_utilities
import random


def cursed_energy(player_card, current_hit_roll, battle_config):
    crit = current_hit_roll
    if player_card.universe == "Jujutsu Kaisen":
        crit = current_hit_roll
        if not player_card.jujutsu_kaisen_focus_crit_used:
            crit = 20
            player_card.jujutsu_kaisen_focus_crit_used = True
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} is preparing their cursed energy for a critical hit")
        if player_card.used_resolve and crit <= 1:
            crit = 10
        return crit
    return crit
        
def cursed_energy_reset(player_card, battle_config):
    if player_card.universe == "Jujutsu Kaisen":
        player_card.jujutsu_kaisen_focus_crit_used = False
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} has reset their cursed energy")
        return
