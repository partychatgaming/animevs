import crown_utilities
import random

def unison_raid(player_card, battle_config, opponent_card, player_title):
    if player_card.universe == "Fairy Tail":  # Fairy Tail Trait
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
        damage_calculation_response_special = player_card.damage_cal(2, battle_config, opponent_card)
        damage_calculation_response_summon = player_card.damage_cal(6, battle_config, opponent_card)
        damage_calculation_response_ultimate = player_card.damage_cal(3, battle_config, opponent_card)
        opponent_card.health = opponent_card.health - (damage_calculation_response_special['DMG'] + damage_calculation_response_summon['DMG'] + damage_calculation_response_ultimate['DMG'])
        player_card.damage_dealth = player_card.damage_dealt + (1)
        player_card.fairy_tail_recovering = True
        player_card.fairy_tail_recovering_duration = 1

        player_card.used_resolve = True
        player_card.usedsummon = False
        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} 🩸 resolved and used their unison raid attack dealing {round(damage_calculation_response_special['DMG'] + damage_calculation_response_summon['DMG'] + damage_calculation_response_ultimate['DMG']):,} damage {title_message}")
        battle_config.next_turn()
        return True
    

def fairy_tail_recovery(player_card, battle_config):
    if player_card.universe == "Fairy Tail" and player_card.fairy_tail_recovering:
        if player_card.fairy_tail_recovering_duration > 0:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} is recovering from their unison raid attack")
            battle_config.next_turn()
        if player_card.fairy_tail_recovering_duration == 0:
            player_card.fairy_tail_recovering = False
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} has recovered from their unison raid attack")
        player_card.fairy_tail_recovering_duration = player_card.fairy_tail_recovering_duration - 1
        return 
    

def concentration(player_card, battle_config):
    if player_card.universe == "Fairy Tail":
        player_card.card_lvl_ap_buff = player_card.card_lvl_ap_buff + (20 * player_card.tier) * player_card.focus_count
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} gains {(20 * player_card.tier) * player_card.focus_count} AP from their concentration")
        return

