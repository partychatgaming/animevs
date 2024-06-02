import crown_utilities
import random


def rulers_authority(player_card, battle_config, opponent_card):
    if player_card.universe == "Solo Leveling":
        opponent_card.defense = round(opponent_card.defense - ((40 + battle_config.turn_total) * player_card.tier))
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {opponent_card.name} defense decreased by {(40 + battle_config.turn_total) * player_card.tier} 🛡️ 🔻 due to ruler's authority")


def set_solo_leveling_config(player_card, opponent_shield_active, opponent_shield_value, opponent_barrier_active, opponent_barrier_value, opponent_parry_active, opponent_parry_value):
    if player_card.universe == "Solo Leveling":
        player_card.solo_leveling_trait_active = True 
        if opponent_shield_active and player_card.temp_opp_shield_value <= 0:
            player_card.temp_opp_arm_shield_active = True
            player_card.temp_opp_shield_value += opponent_shield_value
        
        if opponent_barrier_active and player_card.temp_opp_barrier_value <= 0:
            player_card.temp_opp_arm_barrier_active = True
            player_card.temp_opp_barrier_value += opponent_barrier_value
        
        if opponent_parry_active and player_card.temp_opp_parry_value <= 0:
            player_card.temp_opp_arm_parry_active = True
            player_card.temp_opp_parry_value += opponent_parry_value


def add_solo_leveling_temp_values(player_card, protection, opponent_card):
    if opponent_card.universe == "Solo Leveling":
        if protection == "BARRIER":
            opponent_card.temp_opp_arm_barrier_active = True
            opponent_card.temp_opp_barrier_value += player_card._barrier_value

        if protection == "SHIELD":
            opponent_card.temp_opp_arm_shield_active = True
            opponent_card.temp_opp_shield_value += player_card._shield_value
        
        if protection == "PARRY":
            opponent_card.temp_opp_arm_parry_active = True
            opponent_card.temp_opp_parry_value += player_card._parry_value


def decrease_solo_leveling_temp_values_self(player_card, protection, battle_config):
    if player_card.universe == "Solo Leveling":
        if protection == "BARRIER":
            player_card.barrier_active = True
            player_card._barrier_value = player_card.temp_opp_barrier_value
            player_card.temp_opp_arm_barrier_active = False
            player_card.temp_opp_barrier_value = 0

        if protection == "SHIELD":
            player_card.shield_active = True
            player_card._shield_value = player_card.temp_opp_shield_value
            player_card.temp_opp_arm_shield_active = False
            player_card.temp_opp_shield_value = 0
        
        if protection == "PARRY":
            player_card.parry_active = True
            player_card._parry_value = player_card.temp_opp_parry_value
            player_card.temp_opp_arm_parry_active = True
            player_card.temp_opp_parry_value = 0

        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} arise, ressurrecting their opponent's arm")


def decrease_solo_leveling_temp_values(player_card, protection, opponent_card, battle_config):
    if opponent_card.universe == "Solo Leveling":
        if protection == "BARRIER":
            opponent_card.barrier_active = True
            opponent_card._barrier_value = opponent_card.temp_opp_barrier_value
            opponent_card.temp_opp_arm_barrier_active = False
            opponent_card.temp_opp_barrier_value = 0

        if protection == "SHIELD":
            opponent_card.shield_active = True
            opponent_card._shield_value = opponent_card.temp_opp_shield_value
            opponent_card.temp_opp_arm_shield_active = False
            opponent_card.temp_opp_shield_value = 0
        
        if protection == "PARRY":
            opponent_card.parry_active = True
            opponent_card._parry_value = opponent_card.temp_opp_parry_value
            opponent_card.temp_opp_arm_parry_active = True
            opponent_card.temp_opp_parry_value = 0

        battle_config.add_to_battle_log(f"🩸 {opponent_card.name} arise, ressurrecting your arm")


def activate_solo_leveling_trait(player_card, battle_config, opponent_card):
    # Make sure that if opponent shield, barrier, or parry breaks you gain that temp value
    if player_card.universe == "Solo Leveling":
        if opponent_card.temp_opp_arm_shield_active and not opponent_card.shield_active:
            if player_card.shield_active:
                player_card._shield_value = player_card._shield_value + opponent_card._shield_value
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} arise, {opponent_card.name}'s shield is now yours")
                player_card.solo_leveling_trait_swapped = True
            elif not player_card.shield_active:
                player_card.shield_active = True
                player_card._shield_value = opponent_card.temp_opp_shield_value
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} arise, {opponent_card.name}'s shield is now yours")
                player_card.solo_leveling_trait_swapped = True
        
        elif opponent_card.temp_opp_arm_parry_active and not opponent_card.barrier_active:
            if player_card.barrier_active:
                player_card._barrier_value = player_card._barrier_value + opponent_card.temp_opp_barrier_value
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} arise, {opponent_card.name}'s parry is now yours'")
                player_card.solo_leveling_trait_swapped = True
            elif not player_card.barrier_active:
                player_card.barrier_active = True
                player_card._barrier_value = opponent_card.temp_opp_barrier_value
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} arise, {opponent_card.name}'s parry is now yours")
                player_card.solo_leveling_trait_swapped = True
        
        elif opponent_card.temp_opp_arm_parry_active and not opponent_card._parry_value:
            if player_card.parry_active:
                player_card._parry_value = player_card._parry_value + opponent_card.temp_opp_parry_value
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} arise, {opponent_card.name}'s parry is now yours")
                player_card.solo_leveling_trait_swapped = True
            elif not player_card.parry_active:
                player_card.parry_active = True
                player_card._parry_value = opponent_card.temp_opp_parry_value
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} arise, {opponent_card.name}'s parry is now yours")
                player_card.solo_leveling_trait_swapped = True


