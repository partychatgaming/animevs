import crown_utilities
import random

def fear(player_card, battle_config, opponent_card, player_title):
    if player_card.universe == "Overlord":  # Overlord Trait
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

        player_card.used_resolve = True
        player_card.usedsummon = False
        battle_config.turn_total = battle_config.turn_total + 1
        player_card.overlord_fear_bool = True
        player_card.overlord_fear_duration = player_card.tier * 1
        player_card.overlord_opponent_original_defense = opponent_card.defense
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} ♾️ resolved and caused {opponent_card.name} to succumb to fear, lowering their defense to 25 for {player_card.overlord_fear_duration} turns {title_message}")
        battle_config.next_turn()
        return True
    

def fear_duration_check(player_card, battle_config):
    if player_card.universe == "Overlord" and player_card.overlord_fear_bool:
        if player_card.fairy_tail_recovering_duration > 0:
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} is recovering from their unison raid attack")
            battle_config.next_turn()
        if player_card.fairy_tail_recovering_duration == 0:
            player_card.fairy_tail_recovering = False
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} has recovered from their unison raid attack")
        player_card.fairy_tail_recovering_duration = player_card.fairy_tail_recovering_duration - 1
        return 
    

def fear_aura(player_card, opponent_card, battle_config):
    if player_card.universe == "Overlord":
        def apply_damage_and_ensure_minimum(attr, damage, min_value=50):
            new_value = attr - damage
            return max(min_value, new_value)
        debuff_value = player_card.tier * 20
        opponent_card.move1base = apply_damage_and_ensure_minimum(opponent_card.move1base, debuff_value)
        opponent_card.move2base = apply_damage_and_ensure_minimum(opponent_card.move2base, debuff_value)
        opponent_card.move3base = apply_damage_and_ensure_minimum(opponent_card.move3base, debuff_value)

        # Ensure minimum value for card level AP buff
        opponent_card.card_lvl_ap_buff = max(25, opponent_card.card_lvl_ap_buff)        
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name}'s aura causes {opponent_card.name} to succumb to fear, lowering their AP by {debuff_value}")
        return

